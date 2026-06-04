import React from 'react';

const SourceCitation = ({ source }) => {
  const [expanded, setExpanded] = React.useState(false);

  return (
    <div className="inline-flex items-center gap-2 px-2 py-1 bg-teal-100 text-teal-700 rounded text-xs font-medium cursor-pointer hover:bg-teal-200 transition">
      <span>Page {source.page_num}</span>
      {source.relevance_score && (
        <span className="text-teal-600">
          ({(source.relevance_score * 100).toFixed(0)}%)
        </span>
      )}
    </div>
  );
};

export default SourceCitation;
