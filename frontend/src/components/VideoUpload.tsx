'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from './ui/button'

export default function VideoUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]

      if (file.size > MAX_FILE_SIZE) {
        setErrorMessage('File size exceeds 50MB limit.')
        setSelectedFile(null)
        setVideoUrl(null)
        return
      }

      setSelectedFile(file)
      setErrorMessage(null)

      // Generate a preview URL for the video
      const url = URL.createObjectURL(file)
      setVideoUrl(url)
    }
  }, [])

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)

    const formData = new FormData()
    formData.append('video', selectedFile)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      console.log('Success:', data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setUploading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi']
    },
    maxFiles: 1,
    multiple: false, // Ensures only one file is selectable at a time
  })

  return (
    <div className="space-y-4">
      {/* Drag & Drop Upload Box */}
      <div 
        {...getRootProps()} 
        className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-primary transition-colors"
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the video here ...</p>
        ) : (
          <div>
            <p>Drag & drop a video here, or click to select</p>
            <Button variant="outline">Select Video</Button>
          </div>
        )}
      </div>

      {/* Show Error Message if File is Too Large */}
      {errorMessage && <p className="text-red-500">{errorMessage}</p>}

      {/* Video Preview (Limited Size) */}
      {videoUrl && (
        <div className="mt-4">
          <p className="font-semibold">Preview:</p>
          <video 
            src={videoUrl} 
            controls 
            className="w-[800px] h-[600px] rounded-lg border shadow-md"
          />
        </div>
      )}

      {/* Upload Button */}
      {selectedFile && (
        <Button onClick={handleUpload} disabled={uploading}>
          {uploading ? 'Uploading...' : 'Upload Video'}
        </Button>
      )}
    </div>
  )
}
