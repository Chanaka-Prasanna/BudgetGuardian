"use client";

import React, { useState, useEffect } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  Pin,
  InfoWindow,
} from "@vis.gl/react-google-maps";

interface Place {
  id: string;
  name: string;
  lat: number;
  lng: number;
  rating: number;
  address: string;
  type?: string;
  price_level?: string;
}

interface MapComponentProps {
  places: Place[];
}

// Color mapping for different place types
const getMarkerColor = (
  type: string = "hotel",
  isSelected: boolean = false
) => {
  if (isSelected) return "#2563eb"; // Blue for selected

  // Normalize type to lowercase for consistent matching
  const normalizedType = type.toLowerCase();

  if (normalizedType.includes("hotel") || normalizedType.includes("lodging")) {
    return "#10b981"; // Green
  } else if (normalizedType.includes("restaurant") || normalizedType.includes("cafe") || normalizedType.includes("food")) {
    return "#f59e0b"; // Orange
  } else if (normalizedType.includes("temple") || normalizedType.includes("heritage") || normalizedType.includes("church") || normalizedType.includes("mosque")) {
    return "#8b5cf6"; // Purple
  } else if (normalizedType.includes("attraction") || normalizedType.includes("landmark")) {
    return "#8b5cf6"; // Purple
  } else if (normalizedType.includes("museum")) {
    return "#8b5cf6"; // Purple
  } else if (normalizedType.includes("park")) {
    return "#10b981"; // Green
  } else if (normalizedType.includes("activity")) {
    return "#ec4899"; // Pink
  } else {
    return "#6b7280"; // Gray for unknown
  }
};

export function MapComponent({ places }: MapComponentProps) {
  const [activePlaceId, setActivePlaceId] = useState<string | null>(null);
  const [currentLocation, setCurrentLocation] = useState<{
    lat: number;
    lng: number;
  } | null>(null);

  // Get user's current location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.log("Could not get current location:", error);
        }
      );
    }
  }, []);

  // Default center - use current location if available, otherwise default to Paris
  const defaultCenter = currentLocation || { lat: 48.8566, lng: 2.3522 };
  const center =
    places.length > 0
      ? { lat: places[0].lat, lng: places[0].lng }
      : defaultCenter;

  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

  if (!apiKey) {
    return (
      <div className="w-full h-full rounded-xl overflow-hidden shadow-lg border border-gray-200 bg-gray-100 flex flex-col items-center justify-center p-6 text-center">
        <div className="bg-red-100 text-red-800 p-4 rounded-full mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-8 h-8"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-bold text-gray-900 mb-2">
          Google Maps API Key Missing
        </h3>
        <p className="text-sm text-gray-600 max-w-sm">
          Please create a{" "}
          <code className="bg-gray-200 px-1 py-0.5 rounded">.env.local</code>{" "}
          file in the frontend directory with your API key:
        </p>
        <div className="mt-4 bg-gray-800 text-gray-100 p-3 rounded text-xs font-mono text-left w-full max-w-sm overflow-x-auto">
          NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_key_here
        </div>
        <p className="mt-4 text-xs text-gray-500">
          Don't forget to restart the server after adding the file!
        </p>
      </div>
    );
  }

  return (
    <APIProvider apiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ""}>
      <div className="w-full h-full rounded-xl overflow-hidden shadow-lg border border-gray-200 relative">
        <Map
          defaultZoom={13}
          defaultCenter={defaultCenter}
          center={center}
          mapId="DEMO_MAP_ID" // Required for AdvancedMarker
          className="w-full h-full"
        >
          {/* Current Location Marker */}
          {currentLocation && (
            <AdvancedMarker position={currentLocation} title="Your Location">
              <Pin
                background="#ef4444"
                borderColor="#991b1b"
                glyphColor={"#fff"}
                scale={1.3}
              />
            </AdvancedMarker>
          )}

          {/* Place Markers */}
          {places.map((place, index) => {
            const markerColor = getMarkerColor(place.type, false);

            return (
              <AdvancedMarker
                key={place.id}
                position={{ lat: place.lat, lng: place.lng }}
                onClick={() => setActivePlaceId(place.id)}
                title={place.name}
              >
                <div className="relative">
                  <Pin
                    background={markerColor}
                    borderColor="#000"
                    glyphColor={"#fff"}
                    scale={1.0}
                  />
                  <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-white px-2 py-0.5 rounded shadow text-xs font-bold whitespace-nowrap">
                    {index + 1}
                  </div>
                </div>
              </AdvancedMarker>
            );
          })}

          {activePlaceId &&
            (() => {
              const activePlace = places.find((p) => p.id === activePlaceId);
              if (!activePlace) return null;

              return (
                <InfoWindow
                  position={{ lat: activePlace.lat, lng: activePlace.lng }}
                  onCloseClick={() => setActivePlaceId(null)}
                >
                  <div className="p-2 max-w-xs">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-bold text-gray-900">
                          {activePlace.name}
                        </h3>
                        <span className="inline-block px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-700 capitalize">
                          {activePlace.type || "place"}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      {activePlace.address}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-yellow-600 font-medium">
                        ★ {activePlace.rating}
                      </span>
                      <span className="text-xs text-gray-500">
                        #{places.findIndex((p) => p.id === activePlaceId) + 1}
                      </span>
                    </div>
                  </div>
                </InfoWindow>
              );
            })()}
        </Map>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur rounded-lg shadow-lg p-3 text-xs">
          <div className="font-bold text-gray-800 mb-2">Legend</div>
          <div className="space-y-1">
            {currentLocation && (
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: "#ef4444" }}
                ></div>
                <span className="text-gray-700">Your Location</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: "#10b981" }}
              ></div>
              <span className="text-gray-700">Hotels</span>
            </div>
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: "#8b5cf6" }}
              ></div>
              <span className="text-gray-700">Attractions/Heritage</span>
            </div>
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: "#f59e0b" }}
              ></div>
              <span className="text-gray-700">Restaurants</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-400"></div>
              <span className="text-gray-700">Other Places</span>
            </div>
            {places.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-600">
                {places.length} locations found
              </div>
            )}
          </div>
        </div>
      </div>
    </APIProvider>
  );
}
