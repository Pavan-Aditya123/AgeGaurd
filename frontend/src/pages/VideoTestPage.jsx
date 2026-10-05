/**
 * pages/VideoTestPage.jsx  [TEMPORARY DEBUG PAGE]
 *
 * Visit /video-test to see exactly what URL is being loaded for each movie's video.
 * Remove this page after debugging is complete.
 */

import React, { useState } from "react";
import MOVIES from "../data/movies";

export default function VideoTestPage() {
  const [activeId, setActiveId] = useState(MOVIES[0].id);
  const activeMovie = MOVIES.find((m) => m.id === activeId);
  const encodedUrl = activeMovie?.video ? encodeURI(activeMovie.video) : null;

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <h1 className="text-2xl font-bold mb-2">Video URL Debug Page</h1>
      <p className="text-white/50 text-sm mb-8">Temporary page — remove after debugging.</p>

      {/* Movie selector */}
      <div className="flex flex-wrap gap-2 mb-8">
        {MOVIES.map((m) => (
          <button
            key={m.id}
            onClick={() => setActiveId(m.id)}
            className={`px-3 py-1.5 rounded text-sm border ${
              m.id === activeId
                ? "bg-white text-black border-white"
                : "bg-white/10 border-white/20 hover:bg-white/20"
            }`}
          >
            {m.title}
          </button>
        ))}
      </div>

      {/* URL info */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-6 max-w-2xl">
        <p className="text-white/50 text-xs uppercase tracking-widest mb-1">Movie</p>
        <p className="text-white text-lg font-semibold mb-4">{activeMovie?.title}</p>

        <p className="text-white/50 text-xs uppercase tracking-widest mb-1">Raw video field</p>
        <code className="block text-green-400 text-sm mb-4 break-all">
          {activeMovie?.video ?? "—"}
        </code>

        <p className="text-white/50 text-xs uppercase tracking-widest mb-1">Encoded URL (used in src)</p>
        <code className="block text-yellow-400 text-sm mb-4 break-all">
          {encodedUrl ?? "—"}
        </code>

        <p className="text-white/50 text-xs uppercase tracking-widest mb-1">Restricted</p>
        <p className={`text-sm font-medium ${activeMovie?.restricted ? "text-red-400" : "text-green-400"}`}>
          {String(activeMovie?.restricted)}
        </p>
      </div>

      {/* Live video test */}
      {encodedUrl && (
        <div className="max-w-2xl">
          <p className="text-white/50 text-xs uppercase tracking-widest mb-2">Live player test</p>
          <video
            key={encodedUrl}
            controls
            className="w-full rounded-xl bg-white/5 border border-white/10"
            onError={(e) => console.error("Video error event:", e.nativeEvent)}
            onLoadedData={() => console.log("Video loaded OK:", encodedUrl)}
          >
            <source src={encodedUrl} type="video/mp4" />
            Your browser does not support HTML5 video.
          </video>
          <p className="text-white/30 text-xs mt-2">
            If the video above shows an error, open DevTools → Network tab and check if the request
            for <code className="text-white/50">{encodedUrl}</code> returns 404 or another error.
          </p>
        </div>
      )}
    </div>
  );
}
