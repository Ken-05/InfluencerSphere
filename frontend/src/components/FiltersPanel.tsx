/**
 * FiltersPanel.tsx
 * ----------------
 * Provides UI for filtering influencers by niche, engagement score, etc.
 */

import React, { useState } from "react";

interface Props {
  onFilterChange: (filters: any) => void;
}

const FiltersPanel: React.FC<Props> = ({ onFilterChange }) => {
  const [niche, setNiche] = useState("");
  const [minScore, setMinScore] = useState(0);

  const handleApply = () => {
    onFilterChange({ niche, minScore });
  };

  return (
    <div className="flex gap-4 p-2">
      <input
        type="text"
        placeholder="Niche"
        value={niche}
        onChange={(e) => setNiche(e.target.value)}
        className="border p-1 rounded"
      />
      <input
        type="number"
        placeholder="Min Score"
        value={minScore}
        onChange={(e) => setMinScore(Number(e.target.value))}
        className="border p-1 rounded"
      />
      <button onClick={handleApply} className="bg-blue-500 text-white px-3 py-1 rounded">
        Apply
      </button>
    </div>
  );
};

export default FiltersPanel;
