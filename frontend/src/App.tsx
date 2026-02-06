import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import 'leaflet/dist/leaflet.css'
import './App.css'
import Button from './components/Button'
import Input from './components/Input'
import Card, { CardContent, CardHeader } from './components/Card'
import Loading from './components/Loading'
import RouteMap from './components/RouteMap'
import type { RouteNodePayload } from './components/RouteMap'

interface ApiError {
  detail: string
}

interface PlanSection {
  title: string
  details: string[]
}

const SendIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="m22 2-7 20-4-9-9-4 20-7z" />
    <path d="M22 2 11 13" />
  </svg>
)

const CalendarIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
    <line x1="16" y1="2" x2="16" y2="6" />
    <line x1="8" y1="2" x2="8" y2="6" />
    <line x1="3" y1="10" x2="21" y2="10" />
  </svg>
)

const JOURNEY_STATS = [
  { value: '120+', label: 'Cities curated' },
  { value: '4.9/5', label: 'Guest satisfaction' },
  { value: '48 hrs', label: 'Average turn-around' }
]

const JOURNEY_THEMES = [
  'Culinary residencies',
  'Wellness sabbaticals',
  'Culture-deep dives',
  'Remote work escapes'
]

const SHOWCASE_CARDS = [
  {
    title: 'Sample canvas',
    meta: 'Kyoto × Naoshima',
    summary: 'Layered 5-night immersion with art island hop, chef tables, and sunrise rituals.',
    checklist: ['Rail sync with seat maps', 'Wellness cadence locked', 'Nightlife buffer windows']
  },
  {
    title: 'Signal stack',
    meta: 'Modules active',
    summary: 'AI monitors watching this workspace in realtime.',
    checklist: ['Weather pulse', 'Route intelligence', 'Budget guard', 'Sustainability delta']
  }
]

const SUGGESTIONS = [
  'Design a 5-day culinary retreat through Osaka for two foodies in spring',
  'Weekend wellness escape near Lisbon with spa hotels and coastal hikes',
  'Plan a remote-work friendly month in Buenos Aires with coworking passes',
  'Craft a winter adventure through the Swiss Alps for a family of four'
]

const JOURNEY_STEPS = [
  {
    step: '01',
    title: 'Share the vibe',
    copy: 'Tell the concierge about travellers, timeframe, and desired energy.'
  },
  {
    step: '02',
    title: 'Refine effortlessly',
    copy: 'Iterate on dining, stays, or logistics with natural language tweaks.'
  },
  {
    step: '03',
    title: 'Book with confidence',
    copy: 'Export curated blueprints into your booking stack and go.'
  }
]

const PLAN_TABS = [
  { id: 'itinerary', label: 'Itinerary detail' },
  { id: 'moments', label: 'Key moments' },
  { id: 'mood', label: 'Mood board' },
  { id: 'locale', label: 'Locale brief' }
] as const

type PlannerTabId = (typeof PLAN_TABS)[number]['id']

const EXPERIENCE_TOGGLES = [
  { id: 'liveWeather', label: 'Weather pulse', description: 'Surface micro-climates & packing cues', icon: '🌤️' },
  { id: 'mapLayers', label: 'Route map', description: 'Plot multi-city arcs with transfers', icon: '🗺️' },
  { id: 'budgetGuard', label: 'Budget guard', description: 'Track spend tiers + risk alerts', icon: '💳' },
  { id: 'localHosts', label: 'Local hosts', description: 'Embed fixers, tastemakers, guides', icon: '🤝' },
  { id: 'wellnessSync', label: 'Wellness sync', description: 'Balance recovery, nutrition, tempo', icon: '🧘' },
  { id: 'sustainMode', label: 'Low-impact', description: 'Bias rail + EV transfers', icon: '🌿' }
] as const

type PlannerToggleId = (typeof EXPERIENCE_TOGGLES)[number]['id']

type PlannerLayerSettings = Record<PlannerToggleId, boolean>

interface WeatherSnapshot {
  label?: string
  tempC?: number
  description?: string
  rainChance?: number
}

interface WeatherBlock {
  location: string
  summary?: string
  high?: number
  low?: number
  condition?: string
  humidity?: number
  windKph?: number
  daylight?: string
  trend?: string
  rainChance?: number
  forecast?: WeatherSnapshot[]
}

interface RouteMapPayload {
  nodes: RouteNodePayload[]
}

interface BudgetGuardInsight {
  tier: string
  perPerson: string
  totalRange: string
  riskAlerts: string[]
  recommendedSplits: string[]
  currencyCode?: string
  currencySymbol?: string
  localCurrencyCode?: string
  localCurrencySymbol?: string
  perPersonLocal?: string
  localRange?: string
  conversionRate?: number
}

interface LocalHostProfile {
  name: string
  role: string
  specialty: string
  contactHint: string
  availability: string
}

interface WellnessSyncInsight {
  balanceScore: number
  tempo: string
  anchors: string[]
  recommendations: string[]
}

interface SustainabilityInsight {
  co2Delta: string
  lowImpactMoves: string[]
  energyNotes: string[]
  status: string
}

interface LocaleSummary {
  location: string
  narrative: string
  keyFacts: string[]
  image?: string
  alt: string
  credit?: string
}

interface GalleryImageAsset {
  url: string
  alt?: string
  photographer?: string
  source?: string
}

interface GalleryDisplayImage {
  src: string
  alt: string
  credit?: string
}

interface LocaleBriefPayload {
  summary: string
  highlights: string[]
}

interface TravelPlan {
  answer: string
  itinerary: PlanSection[]
  keyMoments: string[]
  localeBrief?: LocaleBriefPayload | null
  weather?: WeatherBlock
  routeMap?: RouteMapPayload
  budgetGuard?: BudgetGuardInsight
  localHosts?: LocalHostProfile[]
  wellnessSync?: WellnessSyncInsight
  sustainability?: SustainabilityInsight
  galleryImages?: GalleryImageAsset[]
  layers: PlannerLayerSettings
  timestamp: string
  status: string
}

type ApiResponse = TravelPlan

const formatCurrencyValue = (value: number, currencyCode?: string) => {
  if (!currencyCode || Number.isNaN(value)) {
    return value.toFixed(2)
  }
  try {
    return new Intl.NumberFormat(undefined, { style: 'currency', currency: currencyCode }).format(value)
  } catch (err) {
    return `${currencyCode} ${value.toFixed(2)}`
  }
}

function App() {
  const [userInput, setUserInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [travelPlan, setTravelPlan] = useState<TravelPlan | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activePlanTab, setActivePlanTab] = useState<PlannerTabId>('itinerary')
  const [activeToggles, setActiveToggles] = useState<Record<PlannerToggleId, boolean>>(() =>
    EXPERIENCE_TOGGLES.reduce((acc, toggle) => {
      acc[toggle.id] = toggle.id === 'liveWeather' || toggle.id === 'mapLayers'
      return acc
    }, {} as Record<PlannerToggleId, boolean>)
  )
  const [converterInput, setConverterInput] = useState('100')

  // Get API URL from environment or use default
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  useEffect(() => {
    setConverterInput('100')
  }, [travelPlan?.timestamp])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(e.target.value)
    setError(null)
  }

  const handleSuggestionSelect = (prompt: string) => {
    setUserInput(prompt)
    setError(null)
  }

  const handleToggleChange = (id: PlannerToggleId) => {
    setActiveToggles(prev => ({
      ...prev,
      [id]: !prev[id]
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!userInput.trim()) return

    setIsLoading(true)
    setError(null)
    setTravelPlan(null)

    try {
      const payload = {
        query: userInput,
        layers: activeToggles
      }

      const response = await axios.post<ApiResponse>(`${API_BASE_URL}/travel/query`, payload)

      if (response.status === 200 && response.data.answer) {
        setTravelPlan(response.data)
      } else {
        setError('Invalid response from server')
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorData = err.response?.data as ApiError
        setError(errorData?.detail || err.message || 'Network error occurred')
      } else {
        setError('An unexpected error occurred')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const formattedAnswer = useMemo(() => {
    if (!travelPlan?.answer) return []
    return travelPlan.answer.split(/\n+/).map(line => line.trim()).filter(Boolean)
  }, [travelPlan])

  const fallbackSections = useMemo<PlanSection[]>(() => {
    if (!formattedAnswer.length) return []

    const sections: PlanSection[] = []
    let current: PlanSection | null = null

    formattedAnswer.forEach(line => {
      const dayMatch = line.match(/^(day\s*\d+[^:]*):?\s*(.*)$/i)
      const headerMatch = line.match(/^(morning|afternoon|evening|highlight|stay|dining|experience)s?:?/i)

      if (dayMatch) {
        if (current) sections.push(current)
        current = {
          title: dayMatch[1].replace(/\s+/g, ' ').replace(/:$/, ''),
          details: dayMatch[2] ? [dayMatch[2]] : []
        }
        return
      }

      if (headerMatch) {
        if (current) sections.push(current)
        current = {
          title: headerMatch[0]
            .replace(/s?:?$/i, '')
            .replace(/^(.)/, (_, first) => first.toUpperCase())
            .concat(' Focus'),
          details: [line.replace(headerMatch[0], '').replace(/^\s*[-:]/, '').trim()]
        }
        return
      }

      if (!current) {
        current = { title: 'Highlights', details: [] }
      }

      current.details.push(line)
    })

    if (current) sections.push(current)

    if (!sections.length && formattedAnswer.length) {
      sections.push({ title: 'Highlights', details: formattedAnswer })
    }

    return sections
  }, [formattedAnswer])

  const planSections = useMemo<PlanSection[]>(() => {
    if (travelPlan?.itinerary?.length) {
      return travelPlan.itinerary
    }
    return fallbackSections
  }, [travelPlan, fallbackSections])

  const enhanceText = (text: string) => {
    return text
      .replace(/\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b/g, '<strong>$1</strong>')
      .replace(/\b(day\s*\d+)\b/gi, '<em>$1</em>')
      .replace(/(?:must|don’t miss|highlight)[:]?\s*(.+)/gi, '<mark>$1</mark>')
  }

  const stripNarrativeNoise = (text: string) =>
    text
      .replace(/<function[^>]*>.*?<\/function>/gi, ' ')
      .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
      .replace(/^[#>*]+\s*/g, '')
      .replace(/^\s*[-•*]\s*/g, '')
      .replace(/\s+/g, ' ')
      .trim()

  const formatMomentEntry = (text: string): string | null => {
    const cleaned = stripNarrativeNoise(text)
    if (!cleaned) return null
    const sentence = cleaned.match(/[^.!?]+[.!?]?/)
    const trimmed = (sentence?.[0] || cleaned).trim()
    if (!trimmed) return null
    return enhanceText(trimmed)
  }

  const fallbackKeyMoments = useMemo(() => {
    const highlightPattern = /(^[-•]|must|don't miss|don’t miss|highlight)/i
    const inlineCandidates = formattedAnswer
      .filter(line => highlightPattern.test(line))
      .map(line => formatMomentEntry(line))
      .filter((entry): entry is string => Boolean(entry))
      .slice(0, 4)

    if (inlineCandidates.length) {
      return inlineCandidates
    }

    const sectionDerived = planSections
      .flatMap(section => section.details)
      .filter(Boolean)
      .map(detail => formatMomentEntry(detail))
      .filter((entry): entry is string => Boolean(entry))
      .slice(0, 4)

    return sectionDerived
  }, [formattedAnswer, planSections])

  const keyMoments = useMemo(() => {
    const normalized = travelPlan?.keyMoments
      ?.map(moment => moment?.trim())
      .filter((moment): moment is string => Boolean(moment))

    if (normalized?.length) {
      const cleaned = normalized
        .map(moment => formatMomentEntry(moment))
        .filter((entry): entry is string => Boolean(entry))
      if (cleaned.length) {
        return cleaned
      }
    }
    return fallbackKeyMoments
  }, [travelPlan, fallbackKeyMoments])

  const probableLocale = useMemo(() => {
    if (travelPlan?.weather?.location) {
      return travelPlan.weather.location
    }
    const source = travelPlan?.answer || userInput
    if (!source) return 'Global'
    const match = source.match(/([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})/)
    return match?.[1] || 'Global'
  }, [travelPlan, userInput])

  const weatherPeek = useMemo(() => {
    if (travelPlan?.weather) {
      const formatTemp = (value?: number) => (typeof value === 'number' ? `${Math.round(value)}°C` : '—')
      const fallbackTemp = travelPlan.weather.forecast?.[0]?.tempC
      const forecastRain = travelPlan.weather.forecast?.find(snap => typeof snap.rainChance === 'number')?.rainChance

      return {
        location: travelPlan.weather.location,
        high: formatTemp(travelPlan.weather.high ?? fallbackTemp),
        low: formatTemp(travelPlan.weather.low ?? fallbackTemp),
        condition: travelPlan.weather.condition || travelPlan.weather.summary || 'Live weather pending',
        rainChance: typeof travelPlan.weather.rainChance === 'number'
          ? `${travelPlan.weather.rainChance}%`
          : (typeof forecastRain === 'number' ? `${forecastRain}%` : '—'),
        daylight: travelPlan.weather.daylight || '—',
        trend: travelPlan.weather.trend || ''
      }
    }

    return {
      location: probableLocale,
      high: '74°F',
      low: '62°F',
      condition: 'Coastal breeze',
      rainChance: '15%',
      daylight: '10h 45m',
      trend: '+2°F vs seasonal'
    }
  }, [probableLocale, travelPlan])

  const resolvedRouteNodes = useMemo<RouteNodePayload[]>(() => {
    if (!travelPlan?.routeMap?.nodes?.length) return []
    return travelPlan.routeMap.nodes.filter(node =>
      typeof node.latitude === 'number' && typeof node.longitude === 'number'
    )
  }, [travelPlan])

  const routeOverview = useMemo(() => {
    if (resolvedRouteNodes.length) {
      return resolvedRouteNodes.map(node => node.label)
    }

    const nodes = planSections
      .map(section => section.title.replace(/Focus/i, '').trim())
      .filter(Boolean)
      .slice(0, 4)
    if (!nodes.length) {
      nodes.push(probableLocale)
    }
    return nodes
  }, [resolvedRouteNodes, planSections, probableLocale])

  const opsInsights = useMemo(() => {
    const segments = Math.max(planSections.length, 1)
    return [
      {
        label: 'Segments',
        value: `${segments}`,
        meta: segments > 3 ? 'Layered journey' : 'Breezy pace'
      },
      {
        label: 'Climate',
        value: `${weatherPeek.high} / ${weatherPeek.low}`,
        meta: weatherPeek.condition
      },
      {
        label: 'Budget window',
        value: travelPlan?.budgetGuard?.totalRange || '$8.4k – $9.8k',
        meta: travelPlan?.budgetGuard?.tier || 'Boutique stays + curated dining'
      }
    ]
  }, [planSections.length, travelPlan?.budgetGuard?.tier, travelPlan?.budgetGuard?.totalRange, weatherPeek])

  const activeFeatures = useMemo(() => (
    EXPERIENCE_TOGGLES.filter(toggle => activeToggles[toggle.id])
  ), [activeToggles])

  const hasRouteMap = resolvedRouteNodes.length > 0

  const fallbackGallery = useMemo<GalleryDisplayImage[]>(() => {
    const baseQuery = resolvedRouteNodes[0]?.label || userInput || 'luxury travel escape'
    const themes = ['skyline dusk', 'boutique hotel interior', 'artisan dining']
    return themes.map((theme, index) => ({
      src: `https://source.unsplash.com/featured/600x40${index}?${encodeURIComponent(`${baseQuery} ${theme}`)}`,
      alt: `${theme} inspiration`,
      credit: 'Unsplash featured feed'
    }))
  }, [resolvedRouteNodes, userInput])

  const galleryFeed = useMemo<GalleryDisplayImage[]>(() => {
    if (travelPlan?.galleryImages?.length) {
      return travelPlan.galleryImages.map((image, index) => ({
        src: image.url,
        alt: image.alt || `${probableLocale} inspiration ${index + 1}`,
        credit: image.photographer
          ? `Photo by ${image.photographer} · ${image.source || 'Unsplash'}`
          : image.source || 'Unsplash'
      }))
    }
    return fallbackGallery
  }, [fallbackGallery, probableLocale, travelPlan])

  const converterOutput = useMemo(() => {
    if (!travelPlan?.budgetGuard?.conversionRate || !travelPlan?.budgetGuard?.localCurrencyCode) {
      return '—'
    }
    const numericInput = parseFloat(converterInput)
    if (Number.isNaN(numericInput)) {
      return '—'
    }
    const converted = numericInput * travelPlan.budgetGuard.conversionRate
    return formatCurrencyValue(converted, travelPlan.budgetGuard.localCurrencyCode)
  }, [converterInput, travelPlan])

  const localeSummary = useMemo<LocaleSummary | null>(() => {
    if (!travelPlan) return null

    const location = travelPlan.weather?.location || probableLocale
    const primaryImage = galleryFeed[0]

    const buildFallback = () => {
      const detailLines = planSections
        .flatMap(section => section.details)
        .map(detail => stripNarrativeNoise(detail))
        .filter(Boolean)

      const baseSource = detailLines.join(' ') || travelPlan.answer || userInput
      if (!baseSource?.trim()) {
        return null
      }

      const fameHooks = detailLines.filter(line => /iconic|famous|skyline|tower|luxury|desert|beach|mall|palace|modern/i.test(line))
      const heritageHooks = detailLines.filter(line => /heritage|historic|history|ancient|old|souk|fort|museum|temple|mosque|bazaar|quarter/i.test(line))
      const signatureHooks = detailLines.filter(line => /dining|chef|market|safari|cruise|festival|art|design|wellness|nightlife|desert/i.test(line))

      const routeSnippet = routeOverview.slice(0, 3).join(' · ') || probableLocale
      const fameFact = fameHooks[0] || `${probableLocale} is known for skyline drama, design landmarks, and statement hospitality.`
      const heritageFact = heritageHooks[0] || `${probableLocale} keeps heritage quarters, galleries, and trading roots alive alongside new builds.`
      const signatureFact = signatureHooks[0] || `Signature experiences: private guides across ${routeSnippet}, sensory dining, and after-dark rituals.`

      const narrative = fameFact
      const keyFacts = Array.from(
        new Set(
          [heritageFact, signatureFact, ...heritageHooks.slice(1, 2), ...signatureHooks.slice(1, 2)].filter(Boolean)
        )
      )

      return { narrative, keyFacts }
    }
    const fallback = buildFallback()
  const llmSummary = travelPlan.localeBrief?.summary?.trim()
  const llmHighlights = travelPlan.localeBrief?.highlights?.map(item => item.trim()).filter(Boolean) ?? []

  if (llmSummary || llmHighlights.length) {
    return {
      location,
      narrative: llmSummary || fallback?.narrative || `${probableLocale} travel brief`,
      keyFacts: llmHighlights.length ? llmHighlights : (fallback?.keyFacts || []),
      image: primaryImage?.src,
      alt: primaryImage?.alt || `${probableLocale} inspiration`,
      credit: primaryImage?.credit
    }
  }

  if (!fallback) {
    return null
  }

  return {
    location,
    narrative: fallback.narrative,
    keyFacts: fallback.keyFacts,
    image: primaryImage?.src,
    alt: primaryImage?.alt || `${probableLocale} inspiration`,
    credit: primaryImage?.credit
  }
}, [galleryFeed, planSections, probableLocale, routeOverview, travelPlan, userInput])

const statusLabel = isLoading
  ? 'Crafting itinerary'
  : travelPlan
    ? 'Itinerary ready'
    : 'Brief the concierge'

const showBudgetGuard = Boolean(travelPlan && travelPlan.layers?.budgetGuard && travelPlan.budgetGuard)
const showLocalHosts = Boolean(travelPlan && travelPlan.layers?.localHosts && travelPlan.localHosts?.length)
const showWellnessSync = Boolean(travelPlan && travelPlan.layers?.wellnessSync && travelPlan.wellnessSync)
const showSustainability = Boolean(travelPlan && travelPlan.layers?.sustainMode && travelPlan.sustainability)
const showLayerPanel = showBudgetGuard || showLocalHosts || showWellnessSync || showSustainability
const canShowLocaleSummary = Boolean(travelPlan && localeSummary)

return (
  <div className="app-shell">
    <div className="background-grid" aria-hidden="true" />
    <div className="background-orb orb-one" aria-hidden="true" />
    <div className="background-orb orb-two" aria-hidden="true" />

    <header className="site-header container">
      <div className="brand-mark">
        <span className="brand-icon" aria-hidden="true">✦</span>
        Atlas Concierge
      </div>
      <nav className="site-nav" aria-label="Primary">
        <a>Experiences</a>
        <a>Concierge</a>
        <a>Studios</a>
      </nav>
      <Button variant="secondary" size="small" type="button">
        Book a demo
      </Button>
    </header>

    <main className="page-body">
      <section className="story-wrap container">
        <div className="story-panel">
          <p className="eyebrow">Premium AI travel studio</p>
          <h1>Design immersive journeys in minutes, not weeks.</h1>
          <p className="lead-copy">
            Feed our AI concierge with the energy you want and receive a cinematic trip blueprint—routes, stays,
            tastings, and logistics, already harmonized for real people.
          </p>

          <div className="hero-actions">
            <Button type="button" size="large" onClick={() => document.getElementById('planner-panel')?.scrollIntoView({ behavior: 'smooth' })}>
              Start planning
            </Button>
            <button type="button" className="ghost-link">
              View sample itinerary
            </button>
          </div>

          <div className="stat-grid">
            {JOURNEY_STATS.map(stat => (
              <div key={stat.label} className="stat-card">
                <span className="stat-value">{stat.value}</span>
                <span className="stat-label">{stat.label}</span>
              </div>
            ))}
          </div>

          <div className="theme-pills" aria-label="Popular journey themes">
            {JOURNEY_THEMES.map(theme => (
              <span key={theme} className="theme-pill">{theme}</span>
            ))}
          </div>
        </div>

        <div className="story-showcase">
          {SHOWCASE_CARDS.map(card => (
            <article key={card.title} className="showcase-card">
              <header>
                <p className="eyebrow">{card.meta}</p>
                <h3>{card.title}</h3>
              </header>
              <p>{card.summary}</p>
              <ul>
                {card.checklist.map(item => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="planner-lab container" id="planner-panel">
        <div className="control-stack">
          <Card variant="elevated" className="planner-card">
            <CardHeader>
              <div className="planner-header">
                <div>
                  <p className="eyebrow">Live concierge workspace</p>
                  <h2>Trip blueprint</h2>
                </div>
                <span className="status-chip">{statusLabel}</span>
              </div>
            </CardHeader>

            <CardContent>
              <form className="planner-form" onSubmit={handleSubmit}>
                <Input
                  label="Trip brief"
                  type="text"
                  value={userInput}
                  onChange={handleInputChange}
                  placeholder="Paint the picture: travellers, dates, budget, non-negotiables"
                  icon={<CalendarIcon />}
                  error={error || undefined}
                  helperText="The more texture you provide, the more cinematic the plan."
                  variant="outlined"
                />

                <div className="form-footer">
                  <p className="form-hint">Include vibe, dates, party size, and must-see experiences.</p>
                  <Button
                    type="submit"
                    disabled={isLoading}
                    isLoading={isLoading}
                    icon={<SendIcon />}
                  >
                    Generate itinerary
                  </Button>
                </div>
              </form>

              {error && (
                <div className="form-alert" role="alert">
                  {error}
                </div>
              )}

              <div className="suggestion-grid" aria-label="Prompt suggestions">
                {SUGGESTIONS.map(suggestion => (
                  <button
                    type="button"
                    key={suggestion}
                    onClick={() => handleSuggestionSelect(suggestion)}
                    className="suggestion-chip"
                  >
                    <span>{suggestion}</span>
                  </button>
                ))}
              </div>
            </CardContent>

            <CardContent className="feature-panel">
              <div className="feature-panel-header">
                <div>
                  <p className="eyebrow">Experience layers</p>
                  <h3>Tell the AI what to prioritize</h3>
                </div>
                <span className="feature-note">Toggles sync with exports + bookings</span>
              </div>
              <div className="toggle-grid">
                {EXPERIENCE_TOGGLES.map(toggle => {
                  const isActive = activeToggles[toggle.id]
                  return (
                    <button
                      type="button"
                      key={toggle.id}
                      className={`toggle-chip ${isActive ? 'active' : ''}`}
                      onClick={() => handleToggleChange(toggle.id)}
                      aria-pressed={isActive}
                    >
                      <span className="toggle-icon" aria-hidden="true">{toggle.icon}</span>
                      <div className="toggle-copy">
                        <strong>{toggle.label}</strong>
                        <p>{toggle.description}</p>
                      </div>
                      <span className="toggle-dot" aria-hidden="true" />
                    </button>
                  )
                })}
              </div>
            </CardContent>

            <CardContent className="intel-panel">
              <div className="intel-grid">
                <article className="intel-card weather-card">
                  <header>
                    <p className="eyebrow">Live weather</p>
                    <h3>{weatherPeek.location}</h3>
                  </header>
                  <div className="weather-stats">
                    <div>
                      <span className="weather-temp">{weatherPeek.high}</span>
                      <span className="weather-meta">Daytime high</span>
                    </div>
                    <div>
                      <span className="weather-temp muted">{weatherPeek.low}</span>
                      <span className="weather-meta">Evening low</span>
                    </div>
                    <div>
                      <span className="weather-tag">{weatherPeek.condition}</span>
                      <span className="weather-meta">Rain {weatherPeek.rainChance}</span>
                    </div>
                  </div>
                  <footer>
                    <span>{weatherPeek.trend}</span>
                    <span>{weatherPeek.daylight} daylight</span>
                  </footer>
                </article>

                <article className="intel-card map-card">
                  <header>
                    <p className="eyebrow">Route layers</p>
                    <h3>Projected path</h3>
                  </header>
                  <div className={`map-preview ${hasRouteMap ? 'has-map' : ''}`}>
                    {hasRouteMap ? (
                      <>
                        <RouteMap nodes={resolvedRouteNodes} />
                        <div className="map-overlay floating">
                          {routeOverview.map((stop, index) => (
                            <div key={`${stop}-${index}`} className="map-node">
                              <span>{stop}</span>
                              {index < routeOverview.length - 1 && <div className="map-line" aria-hidden="true" />}
                            </div>
                          ))}
                        </div>
                      </>
                    ) : (
                      <div className="map-overlay">
                        {routeOverview.map((stop, index) => (
                          <div key={`${stop}-${index}`} className="map-node">
                            <span>{stop}</span>
                            {index < routeOverview.length - 1 && <div className="map-line" aria-hidden="true" />}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <footer>
                    <span>{routeOverview.length} stops active</span>
                    <span>Auto-transfer sync on</span>
                  </footer>
                </article>

                <article className="intel-card ops-card">
                  <header>
                    <p className="eyebrow">Ops console</p>
                    <h3>Live guardrails</h3>
                  </header>
                  <ul>
                    {opsInsights.map(item => (
                      <li key={item.label}>
                        <div>
                          <span className="ops-label">{item.label}</span>
                          <strong>{item.value}</strong>
                        </div>
                        <p>{item.meta}</p>
                      </li>
                    ))}
                  </ul>
                </article>

                <article className="intel-card signal-card">
                  <header>
                    <p className="eyebrow">Signals</p>
                    <h3>Realtime monitors</h3>
                  </header>
                  <div className="signal-grid">
                    <div>
                      <span className="signal-label">Crowd levels</span>
                      <strong>Moderate</strong>
                      <p>Shift a.m. museum slots</p>
                    </div>
                    <div>
                      <span className="signal-label">Wellness sync</span>
                      <strong>In balance</strong>
                      <p>Keep yoga + night market</p>
                    </div>
                    <div>
                      <span className="signal-label">Sustainability</span>
                      <strong>-28% CO₂</strong>
                      <p>Rail + EV transfers locked</p>
                    </div>
                  </div>
                </article>
              </div>
            </CardContent>

            {travelPlan && showLayerPanel && (
              <CardContent className="layer-panel">
                <div className="layer-grid">
                  {showBudgetGuard && travelPlan?.budgetGuard && (
                    <article className="layer-card budget-card">
                      <header>
                        <p className="eyebrow">Budget guard</p>
                        <h3>{travelPlan.budgetGuard.tier}</h3>
                        <span className="budget-pill">{travelPlan.budgetGuard.perPerson} / guest</span>
                      </header>
                      <p className="budget-range">Total window {travelPlan.budgetGuard.totalRange}</p>
                      {travelPlan.budgetGuard.localRange && (
                        <p className="budget-range subtle">Local spend {travelPlan.budgetGuard.localRange}</p>
                      )}
                      {travelPlan.budgetGuard.perPersonLocal && (
                        <p className="budget-range subtle">Per guest local {travelPlan.budgetGuard.perPersonLocal}</p>
                      )}
                      {travelPlan.budgetGuard.currencyCode && travelPlan.budgetGuard.localCurrencyCode && travelPlan.budgetGuard.conversionRate && (
                        <div className="currency-converter">
                          <div className="converter-header">
                            <span>Currency converter</span>
                            <small>{travelPlan.budgetGuard.currencyCode} → {travelPlan.budgetGuard.localCurrencyCode}</small>
                          </div>
                          <div className="converter-input">
                            <span className="converter-code">{travelPlan.budgetGuard.currencyCode}</span>
                            <input
                              type="number"
                              min="0"
                              step="50"
                              value={converterInput}
                              onChange={event => setConverterInput(event.target.value)}
                              aria-label="Amount in base currency"
                              inputMode="decimal"
                              placeholder={travelPlan.budgetGuard.currencySymbol ? `${travelPlan.budgetGuard.currencySymbol}100` : '100'}
                            />
                            <span className="converter-equals" aria-hidden="true">≈</span>
                            <strong>{converterOutput}</strong>
                          </div>
                        </div>
                      )}
                      <ul>
                        {travelPlan.budgetGuard.riskAlerts.map(alert => (
                          <li key={alert}>{alert}</li>
                        ))}
                      </ul>
                      <footer>
                        {travelPlan.budgetGuard.recommendedSplits.map(split => (
                          <span key={split}>{split}</span>
                        ))}
                      </footer>
                    </article>
                  )}

                  {showLocalHosts && travelPlan?.localHosts && (
                    <article className="layer-card host-card">
                      <header>
                        <p className="eyebrow">Local hosts</p>
                        <h3>On-ground fixers</h3>
                      </header>
                      <div className="host-list">
                        {travelPlan.localHosts.slice(0, 3).map(host => (
                          <div key={host.name} className="host-chip">
                            <div>
                              <strong>{host.name}</strong>
                              <span>{host.role}</span>
                            </div>
                            <p>{host.specialty}</p>
                            <footer>
                              <span>{host.contactHint}</span>
                              <span>{host.availability}</span>
                            </footer>
                          </div>
                        ))}
                      </div>
                    </article>
                  )}

                  {showWellnessSync && travelPlan?.wellnessSync && (
                    <article className="layer-card wellness-card">
                      <header>
                        <p className="eyebrow">Wellness sync</p>
                        <h3>{travelPlan.wellnessSync.tempo}</h3>
                      </header>
                      <div className="wellness-score">
                        <span>{travelPlan.wellnessSync.balanceScore}</span>
                        <small>balance score</small>
                      </div>
                      <ul>
                        {travelPlan.wellnessSync.anchors.map(anchor => (
                          <li key={anchor}>{anchor}</li>
                        ))}
                      </ul>
                      <footer>
                        {travelPlan.wellnessSync.recommendations.map(tip => (
                          <span key={tip}>{tip}</span>
                        ))}
                      </footer>
                    </article>
                  )}

                  {showSustainability && travelPlan?.sustainability && (
                    <article className="layer-card sustain-card">
                      <header>
                        <p className="eyebrow">Low-impact mode</p>
                        <h3>{travelPlan.sustainability.status}</h3>
                        <span className="co2-pill">{travelPlan.sustainability.co2Delta}</span>
                      </header>
                      <ul>
                        {travelPlan.sustainability.lowImpactMoves.map(move => (
                          <li key={move}>{move}</li>
                        ))}
                      </ul>
                      <footer>
                        {travelPlan.sustainability.energyNotes.map(note => (
                          <span key={note}>{note}</span>
                        ))}
                      </footer>
                    </article>
                  )}
                </div>
              </CardContent>
            )}
          </Card>
        </div>

        <div className="output-stack">
          <Card variant="default" className="plan-card">
            <CardHeader>
              <div className="plan-card-header">
                <div>
                  <p className="eyebrow">Generated canvas</p>
                  <h2>Itinerary console</h2>
                </div>
                <span className="status-chip">{statusLabel}</span>
              </div>
            </CardHeader>

            <CardContent className="plan-output" aria-live="polite">
              {isLoading && (
                <div className="plan-loading">
                  <Loading message="Assembling experiences..." />
                </div>
              )}

              {!isLoading && travelPlan && (
                <div className="plan-result">
                  <div className="plan-meta">
                    <CalendarIcon />
                    <span>{new Date(travelPlan.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="plan-window">
                    <div className="plan-window-tabs" role="tablist" aria-label="Plan views">
                      {PLAN_TABS.map(tab => (
                        <button
                          key={tab.id}
                          type="button"
                          role="tab"
                          aria-selected={activePlanTab === tab.id}
                          className={`tab ${activePlanTab === tab.id ? 'active' : ''}`}
                          onClick={() => setActivePlanTab(tab.id)}
                        >
                          {tab.label}
                        </button>
                      ))}
                    </div>

                    <div className="plan-window-body" role="tabpanel">
                      {activePlanTab === 'itinerary' && (
                        <div className="plan-sections" aria-live="polite">
                          {planSections.map(section => (
                            <article key={section.title} className="plan-section-card">
                              <header>
                                <p className="eyebrow">Itinerary detail</p>
                                <h3>{section.title}</h3>
                              </header>
                              <ul>
                                {section.details.map((detail, index) => (
                                  <li
                                    key={`${section.title}-${index}`}
                                    dangerouslySetInnerHTML={{ __html: enhanceText(detail) }}
                                  />
                                ))}
                              </ul>
                            </article>
                          ))}
                        </div>
                      )}

                      {activePlanTab === 'moments' && (
                        <div className="plan-moments">
                          {keyMoments.length ? (
                            <div className="moment-card expanded">
                              <p className="eyebrow">Key moments</p>
                              <h3>Don’t miss these beats</h3>
                              <ul>
                                {keyMoments.map((moment, index) => (
                                  <li key={`moment-${index}`} dangerouslySetInnerHTML={{ __html: moment }} />
                                ))}
                              </ul>
                            </div>
                          ) : (
                            <p className="plan-empty">Add more sensory notes in your prompt to unlock curated highlights.</p>
                          )}
                        </div>
                      )}

                      {activePlanTab === 'mood' && (
                        <div className="plan-gallery expanded">
                          <p className="eyebrow">Mood board</p>
                          <h3>Visual inspiration</h3>
                          <div className="gallery-grid">
                            {galleryFeed.map(image => (
                              <figure key={image.src}>
                                <img src={image.src} alt={image.alt} loading="lazy" />
                              </figure>
                            ))}
                          </div>
                        </div>
                      )}

                      {activePlanTab === 'locale' && (
                        <div className="plan-locale">
                          {canShowLocaleSummary && localeSummary ? (
                            <article className="locale-card">
                              <div className="locale-copy">
                                <p className="eyebrow">Locale brief</p>
                                <h3>{localeSummary.location}</h3>
                                <p>{localeSummary.narrative}</p>
                                {localeSummary.keyFacts.length > 0 && (
                                  <ul className="locale-facts">
                                    {localeSummary.keyFacts.map(fact => (
                                      <li key={fact}>{fact}</li>
                                    ))}
                                  </ul>
                                )}
                                <div className="locale-tags">
                                  <span>{probableLocale}</span>
                                  <span>{routeOverview.length} stops mapped</span>
                                </div>
                              </div>
                              {localeSummary.image && (
                                <figure>
                                  <img src={localeSummary.image} alt={localeSummary.alt} loading="lazy" />
                                </figure>
                              )}
                            </article>
                          ) : (
                            <p className="plan-empty">Generate a plan to unlock a live destination brief.</p>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="plan-toggles-summary">
                      <span>Active layers</span>
                      <div>
                        {activeFeatures.length ? (
                          activeFeatures.map(feature => (
                            <span key={feature.id} className="toggle-pill">{feature.label}</span>
                          ))
                        ) : (
                          <span className="toggle-pill muted">No layers selected</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {!isLoading && !travelPlan && (
                <div className="plan-placeholder">
                  <p>Share a quick brief to see a full itinerary draft with stays, dining, pacing, and hidden gems.</p>
                  <ul>
                    <li>Stack multiple cities and constraints in one request.</li>
                    <li>Ask follow-up questions to refine logistics instantly.</li>
                    <li>Export to PDF or your booking flow once satisfied.</li>
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </section>
    </main>

    <section className="step-section">
      <div className="container step-grid">
        {JOURNEY_STEPS.map(step => (
          <div key={step.step} className="step-card">
            <span className="step-index">{step.step}</span>
            <h3>{step.title}</h3>
            <p>{step.copy}</p>
          </div>
        ))}
      </div>
    </section>
  </div>
)
}

export default App