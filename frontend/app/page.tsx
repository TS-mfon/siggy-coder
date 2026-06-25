'use client';
import React from 'react';
import Link from 'next/link';
export default function Home() {
  return (
    <div style={{ padding: '4rem', textAlign: 'center' }}>
      <h1>Siggy Coder Landing</h1>
      <Link href="/dashboard" style={{ color: '#8a4bf1', display: 'block', marginTop: '1rem' }}>Enter Dashboard</Link>
    </div>
  );
}