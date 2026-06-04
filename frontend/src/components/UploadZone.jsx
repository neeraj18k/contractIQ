/**
 * UploadZone.jsx — Premium Upload Experience
 */

import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Upload,
  FileText,
  CheckCircle2,
  Loader2,
  AlertCircle,
} from 'lucide-react';

const MAX_SIZE_MB = 50;

const UploadZone = ({
  onUpload,
  isLoading = false,
  progress = 0,
  uploadDone = false,
}) => {

  const onDrop = useCallback(
    (acceptedFiles, rejectedFiles) => {
      if (isLoading) return;

      if (rejectedFiles.length > 0) return;

      const file = acceptedFiles[0];

      if (file) {
        onUpload(file);
      }
    },
    [isLoading, onUpload]
  );

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
  } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    maxSize: MAX_SIZE_MB * 1024 * 1024,
    disabled: isLoading,
  });

  const stateClasses = (() => {
    if (uploadDone) {
      return `
        border-green-400
        bg-gradient-to-br
        from-green-50
        to-green-100
      `;
    }

    if (isDragReject) {
      return `
        border-red-400
        bg-gradient-to-br
        from-red-50
        to-red-100
      `;
    }

    if (isDragActive) {
      return `
        border-blue-500
        bg-gradient-to-br
        from-blue-50
        to-indigo-50
        scale-[1.01]
      `;
    }

    if (isLoading) {
      return `
        border-blue-300
        bg-gradient-to-br
        from-blue-50
        to-cyan-50
      `;
    }

    return `
      border-slate-300
      bg-white
      hover:border-blue-500
      hover:shadow-2xl
      hover:scale-[1.01]
    `;
  })();

  return (
    <div className="w-full max-w-3xl mx-auto">

      <div
        {...getRootProps()}
        className={`
          relative
          overflow-hidden
          border-2
          border-dashed
          rounded-3xl
          p-12
          text-center
          transition-all
          duration-300
          shadow-lg
          ${stateClasses}
          ${isLoading ? 'cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <input {...getInputProps()} />

        {/* Decorative Blobs */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-0 left-0 w-40 h-40 bg-blue-300/20 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-0 w-40 h-40 bg-indigo-300/20 rounded-full blur-3xl" />
        </div>

        {/* SUCCESS */}
        {uploadDone && (
          <div className="relative z-10 flex flex-col items-center gap-4">

            <CheckCircle2 className="h-16 w-16 text-green-500" />

            <h3 className="text-2xl font-bold text-green-700">
              Contract Processed Successfully
            </h3>

            <p className="text-green-600">
              Launching AI Contract Assistant...
            </p>
          </div>
        )}

        {/* LOADING */}
        {!uploadDone && isLoading && (
          <div className="relative z-10 flex flex-col items-center gap-5">

            <Loader2 className="h-14 w-14 text-blue-600 animate-spin" />

            <div className="w-full max-w-md">

              <div className="flex justify-between text-sm text-slate-500 mb-2">
                <span>
                  {progress < 100
                    ? 'Uploading Contract...'
                    : 'Processing & Embedding Document...'}
                </span>

                <span>{progress}%</span>
              </div>

              <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                <div
                  className="
                    h-full
                    rounded-full
                    bg-gradient-to-r
                    from-blue-500
                    via-cyan-400
                    to-indigo-500
                    transition-all
                    duration-500
                  "
                  style={{
                    width: `${progress}%`,
                  }}
                />
              </div>
            </div>

            <p className="text-slate-500 text-sm">
              {progress < 100
                ? 'Uploading your PDF securely...'
                : 'Generating embeddings and preparing AI analysis...'}
            </p>
          </div>
        )}

        {/* REJECT */}
        {!uploadDone && !isLoading && isDragReject && (
          <div className="relative z-10 flex flex-col items-center gap-4">

            <AlertCircle className="h-14 w-14 text-red-500" />

            <h3 className="text-xl font-semibold text-red-600">
              Invalid File Type
            </h3>

            <p className="text-red-500 text-sm">
              Only PDF files are supported.
            </p>
          </div>
        )}

        {/* DEFAULT / ACTIVE */}
        {!uploadDone && !isLoading && !isDragReject && (
          <div className="relative z-10 flex flex-col items-center gap-5">

            {isDragActive ? (
              <>
                <div className="
                  w-20 h-20
                  rounded-full
                  bg-blue-100
                  flex
                  items-center
                  justify-center
                ">
                  <FileText className="h-10 w-10 text-blue-600" />
                </div>

                <h3 className="text-2xl font-bold text-blue-700">
                  Drop your PDF here
                </h3>

                <p className="text-slate-500">
                  Release to start upload
                </p>
              </>
            ) : (
              <>
                <div
                  className="
                    w-20
                    h-20
                    rounded-full
                    bg-gradient-to-r
                    from-blue-600
                    to-cyan-500
                    flex
                    items-center
                    justify-center
                    shadow-lg
                  "
                >
                  <Upload className="h-10 w-10 text-white" />
                </div>

                <div>

                  <h3 className="text-2xl font-bold text-slate-800">
                    Upload Your Contract
                  </h3>

                  <p className="text-slate-500 mt-2">
                    Drag & drop your PDF contract here
                  </p>

                  <p className="mt-3 text-blue-600 font-medium">
                    or click to browse files
                  </p>
                </div>

                <div className="flex flex-wrap justify-center gap-2 text-xs">
                  <span className="bg-slate-100 px-3 py-1 rounded-full text-slate-600">
                    PDF Only
                  </span>

                  <span className="bg-slate-100 px-3 py-1 rounded-full text-slate-600">
                    Max {MAX_SIZE_MB} MB
                  </span>

                  <span className="bg-slate-100 px-3 py-1 rounded-full text-slate-600">
                    AI Analysis Ready
                  </span>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadZone;