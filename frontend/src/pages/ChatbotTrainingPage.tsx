import React, { useState, useEffect } from 'react'
import { Upload, FileText, Trash2, BookOpen, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'

interface TrainingDocument {
  id: string
  filename: string
  file_type: string
  content_preview: string
  upload_date: string
  chunk_count: number
}

export default function ChatbotTrainingPage() {
  const [documents, setDocuments] = useState<TrainingDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/admin/chatbot/documents', {
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        setDocuments(data.documents)
      }
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(e.target.files)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      setSelectedFiles(files)
    }
  }

  const handleUpload = async () => {
    if (!selectedFiles || selectedFiles.length === 0) {
      setMessage({ type: 'error', text: 'Please select files to upload' })
      return
    }

    setUploading(true)
    setMessage(null)

    try {
      const formData = new FormData()
      for (let i = 0; i < selectedFiles.length; i++) {
        formData.append('files', selectedFiles[i])
      }

      const response = await fetch('/api/admin/chatbot/upload', {
        method: 'POST',
        credentials: 'include',
        body: formData
      })

      const data = await response.json()
      
      if (data.success) {
        setMessage({ 
          type: 'success', 
          text: `✅ Successfully uploaded ${data.processed} file(s) with ${data.total_chunks} chunks. Chatbot is now trained!` 
        })
        setSelectedFiles(null)
        // Clear file input
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
        if (fileInput) fileInput.value = ''
        
        // Refresh documents list
        await fetchDocuments()
      } else {
        setMessage({ type: 'error', text: data.message || 'Upload failed' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error uploading files. Please try again.' })
      console.error('Upload error:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      const response = await fetch(`/api/admin/chatbot/documents/${docId}`, {
        method: 'DELETE',
        credentials: 'include'
      })

      const data = await response.json()
      
      if (data.success) {
        setMessage({ type: 'success', text: 'Document deleted successfully' })
        fetchDocuments()
      } else {
        setMessage({ type: 'error', text: data.message || 'Delete failed' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error deleting document' })
      console.error('Delete error:', error)
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Chatbot Training
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Upload documents to train the diabetes health assistant
          </p>
        </div>
        <BookOpen className="w-12 h-12 text-blue-600" />
      </div>

      {/* Message Alert */}
      {message && (
        <div className={`p-4 rounded-lg flex items-center gap-3 ${
          message.type === 'success' 
            ? 'bg-green-50 border border-green-200 text-green-800' 
            : 'bg-red-50 border border-red-200 text-red-800'
        }`}>
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* Upload Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Upload Training Documents
        </h2>
        
        <div className="space-y-4">
          <div 
            className={`border-2 border-dashed rounded-lg p-8 transition-colors ${
              isDragging 
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                : 'border-gray-300 dark:border-gray-600'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="text-center">
              <Upload className={`w-12 h-12 mx-auto mb-4 ${isDragging ? 'text-blue-600' : 'text-gray-400'}`} />
              <label className="cursor-pointer">
                <span className="text-blue-600 hover:text-blue-700 font-medium">
                  Choose files or drag & drop here
                </span>
                <input
                  type="file"
                  multiple
                  accept=".txt,.pdf,.doc,.docx,.md"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
              <p className="text-sm text-gray-500 mt-2">
                Supported: PDF, TXT, DOC, DOCX, MD (Max 10MB per file)
              </p>
              {selectedFiles && selectedFiles.length > 0 && (
                <div className="mt-4 text-left">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Selected files ({selectedFiles.length}):
                  </p>
                  <ul className="space-y-1">
                    {Array.from(selectedFiles).map((file, index) => (
                      <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        {file.name} ({(file.size / 1024).toFixed(2)} KB)
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          <button
            onClick={handleUpload}
            disabled={!selectedFiles || uploading}
            className={`w-full py-3 px-6 rounded-lg font-medium flex items-center justify-center gap-2 ${
              !selectedFiles || uploading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {uploading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                Upload & Train
              </>
            )}
          </button>
        </div>
      </div>

      {/* Documents List */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Training Documents ({documents.length})
          </h2>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {documents.reduce((sum, doc) => sum + doc.chunk_count, 0)} total chunks
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3 text-gray-600">Loading documents...</span>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">No training documents yet</p>
            <p className="text-sm">Upload PDF, TXT, or DOC files with diabetes information to train the AI chatbot</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <FileText className="w-5 h-5 text-blue-600" />
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {doc.filename}
                      </h3>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {doc.file_type.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
                      {doc.content_preview}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>{doc.chunk_count} chunks</span>
                      <span>•</span>
                      <span>Uploaded: {new Date(doc.upload_date).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete document"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
        <div className="flex gap-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">How Chatbot Training Works</h3>
            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <div className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">1.</span>
                <span>Upload PDF, TXT, DOC, or MD files containing diabetes education, guidelines, or medical information</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">2.</span>
                <span>Documents are automatically split into searchable chunks (800 characters each with overlap)</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">3.</span>
                <span>When patients ask questions, the AI searches your uploaded documents for relevant information</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">4.</span>
                <span>The chatbot combines your training data with its general knowledge to provide accurate answers</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span className="font-medium text-green-700 dark:text-green-400">Changes take effect immediately - test the chatbot widget after uploading!</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
