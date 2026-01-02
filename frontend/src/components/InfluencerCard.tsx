/**
 * InfluencerCard.tsx
 * ------------------
 * Displays a single influencer's info, image, and ML-driven score.
 */


import React from 'react';
import { InfluencerProfile } from '../services/influencerApi';
import { useNavigate } from 'react-router-dom';

interface Props { profile: InfluencerProfile; }

const InfluencerCard: React.FC<Props> = ({ profile }) => {
  const navigate = useNavigate();
  // Generate a deterministic random ID for the placeholder image based on username length
  const imgId = (profile.username.length * 7) % 50;
  const placeholderImage = `https://picsum.photos/id/${imgId}/300/300`;

  return (
    <div
        onClick={() => navigate(`/influencers/${profile.username}`)}
        style={{
            backgroundColor: '#fff', border: '1px solid #DBDBDB', borderRadius: '8px',
            overflow: 'hidden', cursor: 'pointer', transition: 'transform 0.1s'
        }}
        onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.02)')}
        onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1)')}
    >
      <div style={{ display: 'flex', alignItems: 'center', padding: '15px' }}>
        <img src={placeholderImage} style={{ width: '32px', height: '32px', borderRadius: '50%', marginRight: '10px' }} />
        <strong style={{ fontSize: '14px' }}>{profile.username}</strong>
      </div>

      <img src={placeholderImage} style={{ width: '100%', aspectRatio: '1/1', objectFit: 'cover' }} />

      <div style={{ padding: '10px 15px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
            <span style={{color: '#8E8E8E', fontSize: '12px'}}>FOLLOWERS</span>
            <span style={{fontWeight: 'bold'}}>{profile.follower_count.toLocaleString()}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{color: '#8E8E8E', fontSize: '12px'}}>MARKET SCORE</span>
            <span style={{fontWeight: 'bold', color: profile.market_score > 80 ? 'green' : 'black'}}>
                {profile.market_score.toFixed(0)}
            </span>
        </div>
      </div>
    </div>
  );
};
export default InfluencerCard;