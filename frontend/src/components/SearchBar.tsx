/**
 * SearchBar.tsx
 * -------------
 * Input component to search influencers by brand/niche.
 * Calls backend search API and passes results to parent via callback.
 */


import React, { useState } from 'react';

interface Props { onSearch: (q: string) => void; isLoading: boolean; }

const SearchBar: React.FC<Props> = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('');
  return (
    <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
      <input
        type="text" placeholder="Search usernames or keywords..."
        value={query} onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && onSearch(query)}
        style={{ flexGrow: 1, padding: '10px 15px', borderRadius: '25px', border: '1px solid #DBDBDB', background: '#EFEFEF' }}
      />
      <button
        onClick={() => onSearch(query)}
        disabled={isLoading}
        style={{ padding: '0 20px', borderRadius: '4px', border: 'none', background: '#0095F6', color: '#fff', fontWeight: 'bold' }}
      >
        {isLoading ? '...' : 'Search'}
      </button>
    </div>
  );
};
export default SearchBar;