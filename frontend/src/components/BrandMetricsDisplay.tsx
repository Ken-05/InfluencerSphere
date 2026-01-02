/**
 * Dashboard.tsx
 * -------------
 * Main page component displaying top influencers.
 * Fetches all influencers initially and updates search results.
 */

import React, { useEffect, useState } from "react";
import { fetchAllInfluencers, searchInfluencers } from "../services/influencerApi";
import InfluencerCard from "./InfluencerCard";
import SearchBar from "./SearchBar";

interface Influencer {
  username: string;
  score: number;
  imageUrl?: string;
}

const Dashboard: React.FC = () => {
  const [influencers, setInfluencers] = useState<Influencer[]>([]);

  useEffect(() => {
    const loadInfluencers = async () => {
      const data = await fetchAllInfluencers();
      setInfluencers(data.map((i: any) => ({ username: i.username, score: i.quality_score })));
    };
    loadInfluencers();
  }, []);

  const handleSearch = async (keywords: string) => {
    const results = await searchInfluencers(keywords);
    setInfluencers(results.map((i: any) => ({ username: i.username, score: i.score })));
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">InfluencerSphere Dashboard</h1>
      <SearchBar onSearch={handleSearch} />
      <div className="flex flex-wrap">
        {influencers.map((inf) => (
          <InfluencerCard
            key={inf.username}
            username={inf.username}
            score={inf.score}
          />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;

