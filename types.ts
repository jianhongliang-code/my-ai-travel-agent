
export type ServiceCategory = 
    | 'Flight' | 'Train' | 'Chauffeur' | 'Hotel' | 'Dining' | 'Wellness' | 'Guide' | 'Retail' | 'Lounge';

export type AppMode = 'Consumer' | 'Professional';

export interface TravelService {
    id: string;
    category: ServiceCategory;
    title: string;
    description: string;
    providerName: string;
    status: 'Planned' | 'Executing' | 'Confirmed' | 'Completed';
    time: string;
    location: string;
    metadata: {
        stars?: number;
        commission?: number;
        netRate?: number;
        retailRate?: number;
    }; 
}

export interface AuditReport {
    score: number;
    logisticsScore: number;
    aestheticScore: number;
    profitScore: number;
    conflicts: string[];
    logisticsSummary: string;
    commercialAnalysis?: {
        totalCommission: number;
        marginPercentage: number;
        suggestion: string;
    };
    agentComments: {
        logistics?: string;
        lifestyle?: string;
        profit?: string;
    };
    emotionCurve: number[]; // Rhythmic energy levels 0-100
}

export type Location = 
    | 'ROME' | 'MILAN' | 'FLORENCE' | 'VENICE' | 'NAPLES' | 'BOLOGNA' | 'TURIN' | 'PALERMO' | 'BARI' | 'GENOA'
    | 'CORTINA' | 'LIVIGNO' | 'BORMIO' | 'ANTERSELVA' | 'VAL DI FIEMME' | 'VERONA' | 'BOLZANO' | 'TRENTO';

export type POICategory = 'hotel' | 'attraction' | 'restaurant' | 'market' | 'transport' | 'spa' | 'gallery' | 'shop' | 'other';

export interface StopPoint {
    id: string;
    location: Location;
    label: string;
    startAddress?: string;
    endAddress?: string;
    endCategory?: POICategory;
    endStarRating?: number;
    lat?: number;
    lng?: number;
    // AI Native Metadata
    aestheticScore?: number;
    emotionValue?: number; // 0-100
    isGoldenHourPeak?: boolean;
    narrativeText?: string;
    imgUrl?: string;
}

export interface PlaceSuggestion {
    name: string;
    address: string;
    category: POICategory;
    lat?: number;
    lng?: number;
    starRating?: number;
    url?: string;
}

export type AgentRole = 'orchestrator' | 'logistics' | 'scholar' | 'lifestyle' | 'profit';

export interface TravelPlan {
    plan_id: string;
    agent_version: 'v1-balanced' | 'v2-aesthetic-first' | 'v3-profit-seeker';
    total_revenue: number;
    net_profit: number;
    profit_margin: number;
    aesthetic_score: number;
    logic_score: number;
    is_converted: boolean;
    created_at: string;
}

export interface RouteCalculation {
    path: string;
    segments: any[];
    baseDayFee: number;
    excessDistanceKm: number;
    excessDistanceFee: number;
    overtimeHours: number;
    overtimeFee: number;
    grandTotal: number;
    totalDistanceKm: number;
    totalDurationMins: number;
}

// Added missing interfaces for application entities
export interface DriverProfile {
    fullName: string;
    licenseNumber: string;
    nccPermit: string;
    languages: string[];
    verificationStatus: 'verified' | 'pending' | 'unverified';
}

export interface VehicleProfile {
    model: string;
    plate: string;
    insurancePolicy: string;
    year: number;
    capacity: number;
}

export interface CompanyProfile {
    name: string;
    vatNumber: string;
    registeredAddress: string;
    insuranceLimit: string;
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'provider' | 'system' | 'agent';
    text: string;
    timestamp: number;
    agentId?: AgentRole;
}

export interface AgentAction {
    type: string;
    payload: any;
}

export interface BookingOption {
    id: string;
    type: 'Flight' | 'Train';
    provider: string;
    number: string;
    departure: Location;
    arrival: Location;
    departureTime: string;
    arrivalTime: string;
    price: number;
    duration: string;
    class: string;
}
