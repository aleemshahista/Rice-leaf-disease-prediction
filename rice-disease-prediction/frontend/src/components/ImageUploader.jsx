import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { HiCloudUpload, HiPhotograph, HiX } from 'react-icons/hi';

export default function ImageUploader({ onFileSelect, disabled = false }) {
  const [preview, setPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      const error = rejectedFiles[0].errors[0];
      if (error.code === 'file-too-large') {
        alert('File is too large. Maximum size is 10MB.');
      } else if (error.code === 'file-invalid-type') {
        alert('Invalid file type. Only JPEG and PNG are accepted.');
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      if (onFileSelect) onFileSelect(file);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    maxFiles: 1,
    disabled,
  });

  const clearFile = (e) => {
    e.stopPropagation();
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
    setSelectedFile(null);
    if (onFileSelect) onFileSelect(null);
  };

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`relative rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer overflow-hidden
          ${isDragActive
            ? 'border-primary-400 bg-primary-500/10 scale-[1.02]'
            : disabled
              ? 'border-white/10 bg-white/3 cursor-not-allowed opacity-60'
              : 'border-white/15 bg-white/5 hover:border-primary-500/50 hover:bg-white/8'
          }
        `}
      >
        <input {...getInputProps()} />

        <AnimatePresence mode="wait">
          {preview ? (
            <motion.div
              key="preview"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="relative p-4"
            >
              {/* Clear button */}
              <button
                onClick={clearFile}
                className="absolute top-6 right-6 z-10 w-8 h-8 rounded-full bg-black/60 backdrop-blur-sm flex items-center justify-center text-white/70 hover:text-white hover:bg-red-500/80 transition-all duration-300"
              >
                <HiX className="text-sm" />
              </button>

              {/* Image preview */}
              <div className="rounded-xl overflow-hidden bg-black/20">
                <img
                  src={preview}
                  alt="Selected rice leaf"
                  className="w-full h-64 object-contain"
                />
              </div>

              {/* File info */}
              <div className="mt-3 flex items-center gap-2 text-sm text-white/50">
                <HiPhotograph className="text-primary-400" />
                <span className="truncate">{selectedFile?.name}</span>
                <span className="text-white/30">
                  ({(selectedFile?.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="dropzone"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-16 px-6"
            >
              <motion.div
                animate={isDragActive ? { scale: 1.15, y: -5 } : { scale: 1, y: 0 }}
                transition={{ type: 'spring', stiffness: 300 }}
                className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500/20 to-primary-700/20 border border-primary-500/20 flex items-center justify-center mb-4"
              >
                <HiCloudUpload className="text-3xl text-primary-400" />
              </motion.div>

              <h3 className="text-white font-semibold text-lg mb-1">
                {isDragActive ? 'Drop your image here' : 'Upload Rice Leaf Image'}
              </h3>
              <p className="text-white/40 text-sm text-center max-w-xs">
                Drag & drop or click to browse. Supports JPEG and PNG, up to 10MB.
              </p>

              <div className="mt-4 flex items-center gap-3 text-xs text-white/25">
                <span className="px-2 py-1 rounded bg-white/5">JPG</span>
                <span className="px-2 py-1 rounded bg-white/5">PNG</span>
                <span className="px-2 py-1 rounded bg-white/5">≤ 10MB</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
