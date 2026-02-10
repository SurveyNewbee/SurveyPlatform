import React, { useState } from 'react';

interface EditableHeaderProps {
  title: string;
  onSave: (newTitle: string) => void;
  className?: string;
  editButtonClassName?: string;
  readOnly?: boolean;
}

export default function EditableHeader({ 
  title, 
  onSave, 
  className = '', 
  editButtonClassName = '',
  readOnly = false 
}: EditableHeaderProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(title);

  const handleSave = () => {
    if (editedTitle.trim() && editedTitle !== title) {
      onSave(editedTitle.trim());
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedTitle(title);
    setIsEditing(false);
  };

  if (readOnly || !isEditing) {
    return (
      <div className="flex items-center gap-3 group">
        <h3 className={className}>
          {title}
        </h3>
        {!readOnly && (
          <button
            onClick={() => setIsEditing(true)}
            className={`opacity-0 group-hover:opacity-100 transition-opacity text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded ${editButtonClassName}`}
            title="Edit section title"
          >
            ✏️ Edit
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <input
        type="text"
        value={editedTitle}
        onChange={(e) => setEditedTitle(e.target.value)}
        className="flex-1 px-3 py-2 border border-blue-300 rounded text-xl font-semibold focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        autoFocus
        onBlur={handleSave}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            handleSave();
          }
          if (e.key === 'Escape') {
            handleCancel();
          }
        }}
      />
      <button
        onClick={handleSave}
        className="text-sm px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
      >
        Save
      </button>
      <button
        onClick={handleCancel}
        className="text-sm px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
      >
        Cancel
      </button>
    </div>
  );
}
