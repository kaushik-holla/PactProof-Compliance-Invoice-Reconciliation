import React, { useState, useRef, useEffect } from "react";
import { Box } from "../types/api";
import { useAppStore } from "../store/appStore";
import "../styles/components.css";

interface DocViewerProps {
  fileUrl?: string;
  fileName?: string;
  boxes?: Box[];
}

export const DocViewer: React.FC<DocViewerProps> = ({ fileUrl, fileName, boxes = [] }) => {
  const [dimensions, setDimensions] = useState({ width: 800, height: 1000 });
  const imgRef = useRef<HTMLImageElement>(null);
  const { highlightedFieldPath } = useAppStore();

  useEffect(() => {
    if (imgRef.current && imgRef.current.complete) {
      setDimensions({
        width: imgRef.current.naturalWidth,
        height: imgRef.current.naturalHeight,
      });
    }
  }, [fileUrl]);

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setDimensions({
      width: img.naturalWidth,
      height: img.naturalHeight,
    });
  };

  const highlightedBoxes = boxes.filter((b) => b.page === 0);

  return (
    <div className="doc-viewer">
      <h3>Document Preview</h3>

      {fileUrl ? (
        <div className="doc-container">
          <div className="doc-image-wrapper" style={{ width: dimensions.width, height: dimensions.height }}>
            <img
              ref={imgRef}
              src={fileUrl}
              alt="Document"
              onLoad={handleImageLoad}
              style={{ width: "100%", height: "auto" }}
            />

            <svg
              className="overlay-svg"
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
              }}
            >
              {highlightedBoxes.map((box, idx) => (
                <rect
                  key={idx}
                  x={box.left * 100 + "%"}
                  y={box.top * 100 + "%"}
                  width={(box.right - box.left) * 100 + "%"}
                  height={(box.bottom - box.top) * 100 + "%"}
                  fill="rgba(255, 0, 0, 0.2)"
                  stroke="red"
                  strokeWidth="2"
                />
              ))}
            </svg>
          </div>

          <div className="doc-info">
            <small>
              File: {fileName}
              <br />
              Size: {dimensions.width}x{dimensions.height}px
              <br />
              Highlights: {highlightedBoxes.length}
            </small>
          </div>
        </div>
      ) : (
        <div className="placeholder">Upload documents to view here</div>
      )}
    </div>
  );
};

