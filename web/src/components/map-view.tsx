"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { CoordinateItem } from "@/lib/agent";

type MapViewProps = {
  coordinates: CoordinateItem[];
};

// Day-wise color palette definitions (Moved outside component to prevent re-creation)
const DAY_COLORS = [
  { hex: "#8b5cf6", text: "text-violet-400", bg: "bg-violet-500/10", border: "border-violet-500/30", badge: "bg-violet-600" }, // Day 1
  { hex: "#06b6d4", text: "text-cyan-400", bg: "bg-cyan-500/10", border: "border-cyan-500/30", badge: "bg-cyan-600" },     // Day 2
  { hex: "#f59e0b", text: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/30", badge: "bg-amber-600" }, // Day 3
  { hex: "#f43f5e", text: "text-rose-400", bg: "bg-rose-500/10", border: "border-rose-500/30", badge: "bg-rose-600" },     // Day 4
  { hex: "#10b981", text: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/30", badge: "bg-emerald-600" }, // Day 5
  { hex: "#3b82f6", text: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/30", badge: "bg-blue-600" }       // Day 6+
];

const getDayColor = (day: number) => {
  const index = (day - 1) % DAY_COLORS.length;
  return DAY_COLORS[index];
};

// Helper to create a custom color-coded marker icon with day number
const createDayIcon = (day: number) => {
  const color = getDayColor(day);
  return L.divIcon({
    className: `custom-map-day-icon-${day}`,
    html: `
      <div style="
        background-color: ${color.hex}; 
        color: #ffffff; 
        font-weight: 800; 
        font-size: 11px;
        width: 26px; 
        height: 26px; 
        border-radius: 50%; 
        border: 2px solid #ffffff;
        display: flex; 
        align-items: center; 
        justify-content: center; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
      ">
        ${day}
      </div>
    `,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
    popupAnchor: [0, -10]
  });
};

export default function MapView({ coordinates }: MapViewProps) {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Marker[]>([]);
  const segmentsRef = useRef<L.Polyline[]>([]);

  // Create a memoization key based on coordinates values
  const coordinatesKey = JSON.stringify(coordinates);

  // Focus and trigger marker popup when timeline card is clicked
  const focusOnPoint = (lat: number, lng: number, index: number) => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([lat, lng], 13, { animate: true });
      markersRef.current[index]?.openPopup();
    }
  };

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Initialize Leaflet Map once with hardware acceleration features enabled
    if (!mapInstanceRef.current) {
      mapInstanceRef.current = L.map(mapContainerRef.current, {
        zoomControl: true,
        scrollWheelZoom: true,
        fadeAnimation: true,
        zoomAnimation: true,
        markerZoomAnimation: true
      }).setView([20.5937, 78.9629], 5);

      // Using CartoDB Voyager tiles (High-Performance Global CDN, clean modern look)
      L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
      }).addTo(mapInstanceRef.current);
    }

    const map = mapInstanceRef.current;

    // Remove existing markers & segments
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];
    segmentsRef.current.forEach((s) => s.remove());
    segmentsRef.current = [];

    if (coordinates && coordinates.length > 0) {
      const latLngs = coordinates.map((c) => [c.lat, c.lng] as L.LatLngTuple);

      // Add markers with custom synchronized color icons
      coordinates.forEach((c, idx) => {
        const marker = L.marker([c.lat, c.lng], { icon: createDayIcon(c.day) })
          .addTo(map)
          .bindPopup(
            `
            <div style="font-family: inherit; color: #1e293b; padding: 2px;">
              <div style="font-weight: 800; font-size: 12px; color: #0f172a; margin-bottom: 2px;">
                Day ${c.day}: ${c.name}
              </div>
              <div style="font-size: 11px; line-height: 1.4; color: #475569;">
                ${c.description}
              </div>
            </div>
            `
          );
        markersRef.current.push(marker);
      });

      // Draw route connecting lines with day-wise synchronized segment colors
      if (latLngs.length > 1) {
        for (let i = 0; i < latLngs.length - 1; i++) {
          const color = getDayColor(coordinates[i].day);
          const segment = L.polyline([latLngs[i], latLngs[i + 1]], {
            color: color.hex,
            weight: 3,
            dashArray: "6, 8",
            opacity: 0.8,
          }).addTo(map);
          segmentsRef.current.push(segment);
        }
      }

      // Automatically zoom/fit all coordinates in map viewport
      try {
        const bounds = L.latLngBounds(latLngs);
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 12 });
      } catch (err) {
        console.error("Leaflet: bounds fit failed", err);
      }
    }
  }, [coordinatesKey]);

  // Complete cleanup on unmount
  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div className="w-full h-[450px] relative border border-slate-800 rounded-2xl overflow-hidden shadow-inner bg-slate-950 flex flex-col md:flex-row animate-fadeIn">
      {/* Scrollable Day-wise Timeline Sidebar */}
      <div className="w-full md:w-[220px] lg:w-[260px] flex-shrink-0 flex flex-col border-b md:border-b-0 md:border-r border-slate-800 bg-slate-900/10 overflow-y-auto max-h-[160px] md:max-h-full p-4 gap-3 scrollbar-thin">
        <h4 className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mb-1 flex items-center gap-1.5">
          🗺️ Route Timeline
          <span className="text-[8px] font-normal lowercase text-slate-600 bg-slate-950/40 border border-slate-800 px-1 py-0.2 rounded">
            click to focus
          </span>
        </h4>
        <div className="flex flex-col gap-2.5">
          {coordinates.map((c, idx) => {
            const color = getDayColor(c.day);
            return (
              <button
                key={idx}
                type="button"
                onClick={() => focusOnPoint(c.lat, c.lng, idx)}
                className={`text-left p-2.5 rounded-xl border ${color.bg} ${color.border} flex flex-col gap-1 transition-all duration-200 hover:bg-slate-800/40 hover:border-slate-700/60 cursor-pointer`}
              >
                <div className="flex items-center gap-2">
                  <span className={`text-[9px] px-1.5 py-0.5 rounded-full text-white font-bold leading-none ${color.badge}`}>
                    Day {c.day}
                  </span>
                  <span className={`text-[11px] font-bold truncate flex-1 ${color.text}`}>
                    {c.name}
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 leading-relaxed line-clamp-2">
                  {c.description}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Leaflet Map Area */}
      <div className="flex-1 relative h-full min-h-[290px] md:min-h-0">
        <style dangerouslySetInnerHTML={{__html: `
          .leaflet-container {
            background: #f8fafc !important; /* matches cartodb voyager light styling */
          }
          .leaflet-bar {
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
          }
          .leaflet-bar a {
            background-color: #ffffff !important;
            color: #475569 !important;
            border-bottom: 1px solid rgba(226, 232, 240, 0.8) !important;
          }
          .leaflet-bar a:hover {
            background-color: #f1f5f9 !important;
            color: #0f172a !important;
          }
          .leaflet-popup-content-wrapper {
            background: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.15) !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
          }
          .leaflet-popup-tip {
            background: #ffffff !important;
          }
          .leaflet-left .leaflet-control {
            margin-left: 16px !important;
            margin-top: 16px !important;
          }
        `}} />
        <div ref={mapContainerRef} className="w-full h-full" />
      </div>
    </div>
  );
}
