from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Post as PostModel, Comment as CommentModel, Like as LikeModel
from schemas import (
    Post,
    PostCreate,
    PostDetail,
    Comment,
    CommentCreate,
    UserPublic,
    UserProfile,
    UserStats,
)
from auth import get_current_user

router = APIRouter(tags=["community"])  # no prefix → paths like /posts, /users/{id}


def _serialize_user(user: User) -> UserPublic:
    return UserPublic(id=user.id, email=user.email, name=user.name)


def _serialize_post(post: PostModel) -> Post:
    return Post(
        id=post.id,
        content=post.content,
        type=post.type,
        user=_serialize_user(post.user),
        likes_count=len(post.likes),
        comments_count=len(post.comments),
        created_at=post.created_at,
    )


def _serialize_comment(comment: CommentModel) -> Comment:
    return Comment(
        id=comment.id,
        content=comment.content,
        user=_serialize_user(comment.user),
        created_at=comment.created_at,
    )


@router.get("/posts", response_model=List[Post])
def list_posts(db: Session = Depends(get_db)):
    posts = (
        db.query(PostModel)
        .order_by(PostModel.created_at.desc())
        .all()
    )
    return [_serialize_post(p) for p in posts]


@router.get("/posts/{post_id}", response_model=PostDetail)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comments = (
        db.query(CommentModel)
        .filter(CommentModel.post_id == post_id)
        .order_by(CommentModel.created_at.asc())
        .all()
    )
    return PostDetail(
        **_serialize_post(post).model_dump(),
        comments=[_serialize_comment(c) for c in comments],
    )


@router.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = PostModel(
        user_id=current_user.id,
        content=payload.content,
        type=payload.type,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return _serialize_post(post)


@router.patch("/posts/{post_id}/like")
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing = (
        db.query(LikeModel)
        .filter(LikeModel.post_id == post_id, LikeModel.user_id == current_user.id)
        .first()
    )

    if existing:
        db.delete(existing)
        db.commit()
        liked = False
    else:
        like = LikeModel(post_id=post_id, user_id=current_user.id)
        db.add(like)
        db.commit()
        liked = True

    likes_count = (
        db.query(LikeModel)
        .filter(LikeModel.post_id == post_id)
        .count()
    )

    return {"liked": liked, "likes_count": likes_count}


@router.post(
    "/posts/{post_id}/comments",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comment = CommentModel(
        post_id=post_id,
        user_id=current_user.id,
        content=payload.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _serialize_comment(comment)


@router.get("/posts/{post_id}/comments", response_model=List[Comment])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comments = (
        db.query(CommentModel)
        .filter(CommentModel.post_id == post_id)
        .order_by(CommentModel.created_at.asc())
        .all()
    )
    return [_serialize_comment(c) for c in comments]


@router.get("/users/{user_id}", response_model=UserProfile)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    posts = (
        db.query(PostModel)
        .filter(PostModel.user_id == user_id)
        .order_by(PostModel.created_at.desc())
        .all()
    )

    total_posts = len(posts)
    total_comments = db.query(CommentModel).filter(CommentModel.user_id == user_id).count()
    total_likes_received = (
        db.query(LikeModel)
        .join(PostModel, LikeModel.post_id == PostModel.id)
        .filter(PostModel.user_id == user_id)
        .count()
    )

    stats = UserStats(
        total_posts=total_posts,
        total_comments=total_comments,
        total_likes_received=total_likes_received,
    )

    return UserProfile(
        user=_serialize_user(user),
        posts=[_serialize_post(p) for p in posts],
        stats=stats,
    )

@router.delete("/posts/{post_id}", status_code=200)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your post")

    db.delete(post)
    db.commit()
    return {"detail": "Post deleted"}

@router.delete("/comments/{comment_id}", status_code=200)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.get(CommentModel, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your comment")

    db.delete(comment)
    db.commit()
    return {"detail": "Comment deleted"}
