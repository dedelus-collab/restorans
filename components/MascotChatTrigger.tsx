"use client";

import { AniMascot, SpeechBubble, KawaiiIcon } from "./AniMascot";

export function MascotChatTrigger() {
  function openChat() {
    window.dispatchEvent(new CustomEvent("openChat"));
  }

  return (
    <div className="hidden sm:flex flex-col items-center shrink-0 pt-2">
      {/* Floating food chars above */}
      <div className="flex items-end gap-2 mb-1">
        <KawaiiIcon variant="fish" className="w-10 h-10 animate-bounce"
          style={{ animationDelay: "0.15s", animationDuration: "2s" }} />
        <SpeechBubble text="453 restaurants! ★" className="mb-3 mr-2" />
        <KawaiiIcon variant="romantic" className="w-9 h-9 animate-bounce"
          style={{ animationDelay: "0.4s", animationDuration: "2.3s" }} />
      </div>

      {/* Clickable mascot */}
      <div
        onClick={openChat}
        className="relative cursor-pointer group"
        title="Click to chat with the restaurant AI"
      >
        <AniMascot className="w-36 h-auto drop-shadow-sm group-hover:scale-105 transition-transform duration-200" />

        {/* Pulsing green live dot */}
        <span className="absolute top-1 right-1 flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500" />
        </span>

        {/* Always-visible chat hint badge */}
        <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 flex items-center gap-1 bg-gray-900 text-white text-[10px] font-semibold px-2.5 py-1 rounded-full whitespace-nowrap shadow-lg group-hover:bg-blue-600 transition-colors">
          <span>💬</span>
          <span>Ask me!</span>
        </div>
      </div>

      {/* Floating food chars below */}
      <div className="flex gap-4 mt-6">
        <KawaiiIcon variant="kebap" className="w-8 h-8 animate-bounce"
          style={{ animationDelay: "0.6s", animationDuration: "1.9s" }} />
        <KawaiiIcon variant="night" className="w-8 h-8 animate-bounce"
          style={{ animationDelay: "0.1s", animationDuration: "2.1s" }} />
        <KawaiiIcon variant="breakfast" className="w-8 h-8 animate-bounce"
          style={{ animationDelay: "0.5s", animationDuration: "2.4s" }} />
      </div>
    </div>
  );
}
