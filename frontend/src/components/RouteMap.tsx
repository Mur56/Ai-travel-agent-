import { useEffect, useMemo, useRef, useState } from 'react'
import type { Map as LeafletMap, LayerGroup, LatLngExpression } from 'leaflet'

export interface RouteNodePayload {
  label: string
  latitude: number
  longitude: number
  hint?: string
}

interface RouteMapProps {
  nodes: RouteNodePayload[]
  className?: string
}

type LeafletModule = typeof import('leaflet')

let leafletLoader: Promise<LeafletModule> | null = null
const loadLeaflet = () => {
  if (!leafletLoader) {
    leafletLoader = import('leaflet')
  }
  return leafletLoader
}

const RouteMap = ({ nodes, className }: RouteMapProps) => {
  const mapRootRef = useRef<HTMLDivElement | null>(null)
  const mapInstanceRef = useRef<LeafletMap | null>(null)
  const layerGroupRef = useRef<LayerGroup | null>(null)
  const [leaflet, setLeaflet] = useState<LeafletModule | null>(null)

  const validNodes = useMemo(
    () => nodes.filter(node => typeof node.latitude === 'number' && typeof node.longitude === 'number'),
    [nodes]
  )

  useEffect(() => {
    if (typeof window === 'undefined') return
    loadLeaflet().then(module => {
      const resolved = (module as LeafletModule & { default?: LeafletModule }).default || module
      setLeaflet(resolved)
    })
  }, [])

  useEffect(() => {
    if (!leaflet || !mapRootRef.current || mapInstanceRef.current) {
      return
    }

    const map = leaflet.map(mapRootRef.current, {
      closePopupOnClick: false,
      zoomControl: false,
      attributionControl: false
    })

    leaflet.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map)

    mapInstanceRef.current = map

    return () => {
      map.remove()
      mapInstanceRef.current = null
    }
  }, [leaflet])

  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map || !leaflet) return

    if (layerGroupRef.current) {
      layerGroupRef.current.remove()
      layerGroupRef.current = null
    }

    if (!validNodes.length) {
      return
    }

    const group = leaflet.layerGroup().addTo(map)
    layerGroupRef.current = group

    const latLngs = validNodes.map(node => leaflet.latLng(node.latitude, node.longitude))
    leaflet.polyline(latLngs, { color: '#7c6cff', weight: 3, opacity: 0.9 }).addTo(group)

    validNodes.forEach(node => {
      const marker = leaflet.circleMarker([node.latitude, node.longitude], {
        color: '#7c6cff',
        fillColor: '#7c6cff',
        fillOpacity: 0.95,
        radius: 8,
        weight: 2
      })
      marker.bindTooltip(
        `<strong>${node.label}</strong>${node.hint ? `<br/><span>${node.hint}</span>` : ''}`,
        { direction: 'top' }
      )
      marker.addTo(group)
    })

    if (latLngs.length === 1) {
      map.setView(latLngs[0], 8)
    } else {
      const bounds = leaflet.latLngBounds(latLngs as LatLngExpression[])
      map.fitBounds(bounds, { padding: [20, 20] })
    }

    return () => {
      group.remove()
      layerGroupRef.current = null
    }
  }, [leaflet, validNodes])

  if (!leaflet || !validNodes.length) {
    return null
  }

  return <div ref={mapRootRef} className={`route-map ${className ?? ''}`} />
}

export default RouteMap