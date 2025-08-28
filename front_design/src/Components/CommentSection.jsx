import React, { useState, useEffect } from "react";
import axios from "axios";

// Recursive Comment component
const Comment = ({ comment, currentUser, isAdmin, onReply, onDelete }) => {
  const [replying, setReplying] = useState(false);
  const [replyText, setReplyText] = useState("");

  const handleReply = () => {
    if (replyText.trim()) {
      onReply(comment.id, replyText);
      setReplyText("");
      setReplying(false);
    }
  };

  return (
    <div className="ml-4 mt-2 border-l pl-2">
      <p className="font-semibold">{comment.username}</p>
      <p>{comment.content}</p>

      <div className="flex gap-2 text-sm text-gray-500">
        {currentUser && ( // show Reply only if logged in
          <button onClick={() => setReplying(!replying)}>Reply</button>
        )}
        {(currentUser === comment.username || isAdmin) && (
          <button onClick={() => onDelete(comment.id)}>Delete</button>
        )}
      </div>

      {/* Reply form */}
      {replying && (
        <div className="mt-2">
          <textarea
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            className="w-full p-2 border rounded-md"
            placeholder="Write a reply..."
          />
          <button
            onClick={handleReply}
            className="mt-1 px-3 py-1 bg-blue-500 text-white rounded-md"
          >
            Post Reply
          </button>
        </div>
      )}

      {/* Render nested replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="ml-4 mt-2">
          {comment.replies.map((reply) => (
            <Comment
              key={reply.id}
              comment={reply}
              currentUser={currentUser}
              isAdmin={isAdmin}
              onReply={onReply}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const CommentSection = ({ blogId }) => {
  const [comments, setComments] = useState([]);
  const [content, setContent] = useState("");
  const [currentUser, setCurrentUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);

  const fetchCurrentUser = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/auth/user/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
        },
      });
      setCurrentUser(res.data.username);
      setIsAdmin(res.data.is_staff);
    } catch (err) {
      console.error("Not logged in", err);
    }
  };

  const fetchComments = async () => {
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/api/comments/?blog=${blogId}`
      );
      setComments(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;

    try {
      await axios.post(
        "http://127.0.0.1:8000/api/comments/",
        {
          blog: blogId,
          content,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          },
        }
      );
      setContent("");
      fetchComments();
    } catch (err) {
      console.error(err);
    }
  };

  const handleReply = async (parentId, replyText) => {
    try {
      await axios.post(
        "http://127.0.0.1:8000/api/comments/",
        {
          blog: blogId,
          content: replyText,
          parent: parentId, // important for nested replies
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          },
        }
      );
      fetchComments();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/comments/${id}/`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
        },
      });
      fetchComments();
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
    fetchComments();
  }, [blogId]);

  return (
    <div className="p-4 border rounded-md bg-gray-50">
      <h2 className="text-xl font-bold mb-4">Comments</h2>

      {currentUser ? (
        <form onSubmit={handleSubmit} className="mb-4">
          <textarea
            className="w-full p-2 border rounded-md"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Write a comment..."
          />
          <button
            type="submit"
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md"
          >
            Post
          </button>
        </form>
      ) : (
        <p className="text-gray-600">Login to post a comment.</p>
      )}

      <div>
        {comments.length > 0 ? (
          comments.map((comment) => (
            <Comment
              key={comment.id}
              comment={comment}
              currentUser={currentUser}
              isAdmin={isAdmin}
              onReply={handleReply}
              onDelete={handleDelete}
            />
          ))
        ) : (
          <p className="text-gray-500">No comments yet.</p>
        )}
      </div>
    </div>
  );
};

export default CommentSection;
