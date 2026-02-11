import React, { useState, useMemo, useEffect, useRef, createContext, useContext } from 'react';
import { TravelService, StopPoint, Location, PlaceSuggestion, AuditReport, AppMode, DriverProfile, VehicleProfile, CompanyProfile, TravelPlan } from './types';
import RouteMap from './components/RouteMap';
import TravelAgentHub from './components/TravelAgentHub';
import DriverRegistry from './components/DriverRegistry';
import InputSandbox from './components/InputSandbox';
import ItineraryCard from './components/ItineraryCard';
import EmotionCurve from './components/EmotionCurve';
import ParetoFrontierChart from './components/ParetoFrontierChart';
import FlashTransferTool from './components/FlashTransferTool';
import SearchableLocationSelect from './components/SearchableLocationSelect';
import { generateDeepPOIContent, playBase64Audio, runMultiAgentAudit, suggestRefinement, searchAddressSuggestions } from './services/geminiService';
import { translations, Language, languageNames } from './i18n';
import { KM_RATE, OT_RATE } from './constants';

export type CurrencyCode = 'EUR' | 'USD' | 'GBP' | 'CNY' | 'JPY' | 'CHF';

interface CurrencyContextType {
    currency: CurrencyCode;
    setCurrency: (c: CurrencyCode) => void;
    formatPrice: (eurAmount: number) => string;
}

export const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

export const useCurrency = () => {
    const context = useContext(CurrencyContext);
    if (!context) throw new Error("useCurrency must be used within CurrencyProvider");
    return context;
};

interface LanguageContextType {
    lang: Language;
    setLang: (lang: Language) => void;
    t: (key: keyof typeof translations['en']) => string;
}

export const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) throw new Error("useLanguage must be used within LanguageProvider");
    return context;
};

const EXCHANGE_RATES: Record<CurrencyCode, number> = {
    EUR: 1, USD: 1.09, GBP: 0.85, CNY: 7.92, JPY: 164.5, CHF: 0.96
};

const CURRENCY_SYMBOLS: Record<CurrencyCode, string> = {
    EUR: '€', USD: '$', GBP: '£', CNY: '¥', JPY: '¥', CHF: 'CHF'
};

const ScoreGauge: React.FC<{ score: number; label: string; color: string; icon: string }> = ({ score, label, color, icon }) => (
    <div className="flex flex-col items-center gap-4">
        <div className="relative w-32 h-32">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path className="text-gray-100 opacity-10" strokeWidth="2.5" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                <path className={`${color} transition-all duration-1000 ease-out`} strokeWidth="2.5" strokeDasharray={`${score}, 100`} strokeLinecap="round" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <i className={`fa-solid ${icon} text-lg mb-1 opacity-20`}></i>
                <div className="text-3xl font-black tracking-tighter">{score}</div>
            </div>
        </div>
        <span className="text-[10px] font-black uppercase text-gray-500 tracking-[0.3em]">{label}</span>
    </div>
);

const App: React.FC = () => {
    const detectLanguage = (): Language => {
        const bl = navigator.language.toLowerCase();
        if (bl.startsWith('it')) return 'it';
        if (bl.startsWith('zh')) return 'zh';
        return 'en';
    };

    const [lang, setLang] = useState<Language>(detectLanguage());
    const [currency, setCurrency] = useState<CurrencyCode>('EUR');
    const [mode, setMode] = useState<AppMode>('Consumer');
    const [activeTab, setActiveTab] = useState<'itinerary' | 'logistics' | 'safety' | 'analytics'>('itinerary');
    const [tripMainLocation, setTripMainLocation] = useState<Location>('MILAN');
    
    // Driver Registry State
    const [driver, setDriver] = useState<DriverProfile>({
        fullName: 'Giovanni Rossi',
        licenseNumber: 'IT-48291-DL',
        nccPermit: 'NCC-MILAN-2023-902',
        languages: ['Italian', 'English'],
        verificationStatus: 'unverified'
    });
    const [vehicle, setVehicle] = useState<VehicleProfile>({
        model: 'Mercedes-Benz V-Class',
        plate: 'MI 902 AB',
        insurancePolicy: 'IT-SECURE-99021',
        year: 2023,
        capacity: 7
    });
    const [company, setCompany] = useState<CompanyProfile>({
        name: 'Milan Elite Transfers S.r.l.',
        vatNumber: 'IT01234567890',
        registeredAddress: 'Via della Spiga 12, Milan',
        insuranceLimit: '€5,000,000'
    });
    const [uploadedDocs, setUploadedDocs] = useState<any[]>([]);

    const [stops, setStops] = useState<StopPoint[]>([
        { id: 's1', location: 'MILAN', label: 'Castello Sforzesco', emotionValue: 80, aestheticScore: 92, isGoldenHourPeak: true, narrativeText: 'The morning mist clears over the ramparts, revealing layers of Visconti history.', imgUrl: 'https://images.unsplash.com/photo-1520175480921-4edfa0683c2f?auto=format&fit=crop&w=800' },
        { id: 's2', location: 'MILAN', label: 'Galleria Vittorio Emanuele', emotionValue: 40, aestheticScore: 98, isGoldenHourPeak: false, narrativeText: 'Walking through the glass domes, the light refracts into a million crystalline patterns.', imgUrl: 'https://images.unsplash.com/photo-1544013919-4bb4ec30de70?auto=format&fit=crop&w=800' }
    ]);

    const [audit, setAudit] = useState<AuditReport | null>(null);
    const [isRefining, setIsRefining] = useState(false);

    const formatPrice = (eurAmount: number) => {
        const converted = eurAmount * EXCHANGE_RATES[currency];
        const symbol = CURRENCY_SYMBOLS[currency];
        return `${symbol}${converted.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
    };

    const t = (key: keyof typeof translations['en']): string => translations[lang][key] || translations['en'][key];

    useEffect(() => {
        let isMounted = true;
        const triggerRefinement = async () => {
            if (stops.length < 2) return;
            setIsRefining(true);
            const report = await runMultiAgentAudit(stops, [], mode, lang);
            if (isMounted) setAudit(report);
            setIsRefining(false);
        };
        const timer = setTimeout(triggerRefinement, 2000);
        return () => { isMounted = false; clearTimeout(timer); };
    }, [stops, mode]);

    return (
        <LanguageContext.Provider value={{ lang, setLang, t }}>
            <CurrencyContext.Provider value={{ currency, setCurrency, formatPrice }}>
                <div className={`min-h-screen transition-all duration-700 ${mode === 'Professional' ? 'bg-[#f8f9fa]' : 'bg-slate-950'} text-[#37352f] overflow-x-hidden`}>
                    
                    {/* Top Mode Bar */}
                    <div className="bg-black h-12 flex items-center justify-between px-10">
                        <div className="flex gap-10">
                            <button onClick={() => setMode('Consumer')} className={`text-[10px] font-black uppercase tracking-[0.3em] transition-all ${mode === 'Consumer' ? 'text-blue-400' : 'text-gray-600 hover:text-white'}`}>
                                <i className="fa-solid fa-crown mr-2"></i> Client Canvas
                            </button>
                            <button onClick={() => setMode('Professional')} className={`text-[10px] font-black uppercase tracking-[0.3em] transition-all ${mode === 'Professional' ? 'text-emerald-400' : 'text-gray-600 hover:text-white'}`}>
                                <i className="fa-solid fa-briefcase mr-2"></i> Operator Cockpit
                            </button>
                        </div>
                        <div className="flex gap-6">
                            <div className="flex bg-white/5 p-1 rounded-xl">
                                {(['itinerary', 'safety', 'analytics'] as const).map(tab => (
                                    <button 
                                        key={tab} 
                                        onClick={() => setActiveTab(tab)}
                                        className={`px-4 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${activeTab === tab ? 'bg-white text-black' : 'text-gray-500 hover:text-white'}`}
                                    >
                                        {tab}
                                    </button>
                                ))}
                            </div>
                            <div className="w-[1px] h-4 bg-white/10 mx-2 self-center"></div>
                            {(['EUR', 'USD', 'CNY'] as CurrencyCode[]).map(c => (
                                <button key={c} onClick={() => setCurrency(c)} className={`text-[10px] font-black transition-all ${currency === c ? 'text-white' : 'text-gray-600 hover:text-white'}`}>{c}</button>
                            ))}
                        </div>
                    </div>

                    <main className="max-w-[1800px] mx-auto p-10 space-y-20">
                        
                        {activeTab === 'safety' ? (
                            <section className="animate-in fade-in slide-in-from-bottom-10 duration-700">
                                <DriverRegistry 
                                    driver={driver} setDriver={setDriver}
                                    vehicle={vehicle} setVehicle={setVehicle}
                                    company={company} setCompany={setCompany}
                                    uploadedDocs={uploadedDocs} setUploadedDocs={setUploadedDocs}
                                    onVerificationChange={(v) => setDriver(prev => ({...prev, verificationStatus: v ? 'verified' : 'unverified'}))}
                                />
                            </section>
                        ) : activeTab === 'analytics' && mode === 'Professional' ? (
                             <section className="bg-white rounded-[4rem] p-16 shadow-2xl border border-gray-100 animate-in fade-in duration-700">
                                <h2 className="text-4xl font-black mb-10 tracking-tighter">Yield Frontier Analysis</h2>
                                <ParetoFrontierChart data={[]} paretoData={[]} />
                             </section>
                        ) : (
                            <>
                                {/* 1. Inspiration Sandbox (Client Entrance) */}
                                {mode === 'Consumer' && (
                                    <section className="pt-20 animate-in fade-in slide-in-from-top-10 duration-1000">
                                        <header className="text-center mb-16 space-y-4">
                                            <div className="text-[12px] font-black uppercase tracking-[0.6em] text-blue-500">Multimodal Agent Engine</div>
                                            <h1 className="text-7xl font-black tracking-tighter text-white">The Inspiration Canvas</h1>
                                        </header>
                                        <InputSandbox />
                                    </section>
                                )}

                                {/* 2. Strategy Gauges (Operator Entrance) */}
                                {mode === 'Professional' && audit && (
                                    <section className="bg-white rounded-[4rem] p-16 shadow-2xl animate-in zoom-in-95 duration-1000 border border-gray-100">
                                        <div className="flex items-center justify-between mb-16">
                                            <div>
                                                <div className="text-[12px] font-black uppercase tracking-[0.4em] text-emerald-600 mb-2">Omni Agency Dashboard</div>
                                                <h2 className="text-5xl font-black tracking-tighter">Strategic Yield Control</h2>
                                            </div>
                                            <div className="flex gap-12">
                                                <ScoreGauge score={audit.aestheticScore} label="Soul Score" color="text-violet-500" icon="fa-palette" />
                                                <ScoreGauge score={audit.logisticsScore} label="Logic Score" color="text-blue-500" icon="fa-route" />
                                                <ScoreGauge score={audit.profitScore} label="Yield Score" color="text-emerald-500" icon="fa-coins" />
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                                            <div className="bg-slate-50 rounded-[3rem] p-10 border border-gray-100">
                                                <div className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-6">Pareto Frontier Analysis</div>
                                                <div className="h-[300px] bg-white rounded-3xl border border-gray-100 p-4">
                                                    <div className="h-full w-full flex items-center justify-center text-gray-300 italic text-xs">
                                                        Click dots to morph itinerary...
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="space-y-6">
                                                <div className="p-8 bg-emerald-50 rounded-[2.5rem] border border-emerald-100">
                                                    <div className="text-[10px] font-black uppercase text-emerald-600 tracking-widest mb-4">Commercial Arbitrage Suggestion</div>
                                                    <p className="text-lg font-bold text-emerald-900 leading-tight">
                                                        "{audit.commercialAnalysis?.suggestion}"
                                                    </p>
                                                </div>
                                                <div className="p-8 bg-blue-50 rounded-[2.5rem] border border-blue-100">
                                                    <div className="text-[10px] font-black uppercase text-blue-600 tracking-widest mb-4">Logistics Constraint Check</div>
                                                    <p className="text-sm italic text-blue-900 leading-relaxed">
                                                        {audit.agentComments.logistics}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </section>
                                )}

                                {/* 3. The Fluid Split-View Itinerary */}
                                <div className="grid grid-cols-1 xl:grid-cols-12 gap-16">
                                    <div className="xl:col-span-7 space-y-16">
                                        <div className="flex items-center justify-between">
                                            <h3 className={`text-3xl font-black tracking-tight ${mode === 'Consumer' ? 'text-white' : 'text-black'}`}>
                                                The Italian Flow <span className="text-blue-500 text-sm align-top ml-2">Day 1</span>
                                            </h3>
                                            <div className="flex gap-4">
                                                <SearchableLocationSelect value={tripMainLocation} onChange={setTripMainLocation} />
                                            </div>
                                        </div>

                                        <div className={`${mode === 'Consumer' ? 'bg-slate-900/40' : 'bg-white'} p-8 rounded-[3rem] border border-white/5`}>
                                            <EmotionCurve data={audit?.emotionCurve || [20, 80, 40, 90, 30]} />
                                        </div>

                                        <div className="space-y-10">
                                            {stops.map((stop, idx) => (
                                                <div key={stop.id} className="relative group">
                                                    <ItineraryCard stop={stop} index={idx} mode={mode} />
                                                    {idx < stops.length - 1 && (
                                                        <div className="h-20 flex items-center justify-center relative">
                                                            <div className="absolute left-1/2 top-0 bottom-0 w-[1px] bg-gradient-to-b from-blue-600/50 to-transparent"></div>
                                                            <div className="bg-slate-900 border border-white/10 px-6 py-2 rounded-full text-[9px] font-black uppercase tracking-widest text-blue-400 z-10 shadow-xl">
                                                                <i className="fa-solid fa-car mr-2"></i> 🚗 22m <span className="opacity-30 mx-2">|</span> Stress: Low
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="xl:col-span-5 relative">
                                        <div className="sticky top-10 h-[800px] w-full bg-white border-2 border-gray-100 rounded-[4rem] overflow-hidden shadow-2xl">
                                            <RouteMap stops={stops} />
                                            
                                            <div className="absolute bottom-10 left-10 right-10 flex flex-col gap-4 pointer-events-none">
                                                <div className="bg-black/90 backdrop-blur-2xl p-6 rounded-[2.5rem] text-white flex items-center justify-between shadow-3xl pointer-events-auto border border-white/10">
                                                    <div className="flex items-center gap-4">
                                                        <div className="w-10 h-10 bg-blue-600 rounded-2xl flex items-center justify-center">
                                                            <i className="fa-solid fa-location-arrow"></i>
                                                        </div>
                                                        <div>
                                                            <div className="text-[9px] font-black uppercase tracking-widest text-blue-400">Total Distance</div>
                                                            <div className="text-lg font-black tracking-tight">32.4 KM <span className="text-gray-500 font-medium ml-2">~1h 12m</span></div>
                                                        </div>
                                                    </div>
                                                    <button className="bg-white text-black px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-600 hover:text-white transition-all">
                                                        Go Live
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </>
                        )}

                        {/* Global MAS Command Hub */}
                        <div className="fixed bottom-10 right-10 w-96 z-50">
                            <TravelAgentHub mode={mode} services={[]} onExecuteAction={() => {}} />
                        </div>
                    </main>
                </div>
            </CurrencyContext.Provider>
        </LanguageContext.Provider>
    );
};

export default App;