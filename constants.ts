
import { Location } from './types';

export const LOCATIONS: Location[] = [
    'ROME', 'MILAN', 'FLORENCE', 'VENICE', 'NAPLES', 'BOLOGNA', 'TURIN', 'PALERMO', 'BARI', 'GENOA',
    'CORTINA', 'LIVIGNO', 'BORMIO', 'ANTERSELVA', 'VAL DI FIEMME', 'VERONA', 'BOLZANO', 'TRENTO'
];

export const HUB_LOCATIONS: Location[] = ['ROME', 'MILAN', 'FLORENCE', 'VENICE', 'NAPLES', 'BOLOGNA', 'VERONA'];
export const VENUE_LOCATIONS: Location[] = ['CORTINA', 'LIVIGNO', 'BORMIO', 'ANTERSELVA', 'VAL DI FIEMME', 'TURIN', 'PALERMO', 'BARI', 'GENOA'];

export const LOCATION_COORDS: Record<Location, [number, number]> = {
    'ROME': [41.9028, 12.4964],
    'MILAN': [45.4642, 9.1900],
    'FLORENCE': [43.7696, 11.2558],
    'VENICE': [45.4408, 12.3155],
    'NAPLES': [40.8518, 14.2681],
    'BOLOGNA': [44.4949, 11.3426],
    'TURIN': [45.0703, 7.6869],
    'PALERMO': [38.1157, 13.3615],
    'BARI': [41.1171, 16.8719],
    'GENOA': [44.4056, 8.9463],
    'CORTINA': [46.5405, 12.1357],
    'LIVIGNO': [46.5386, 10.1357],
    'BORMIO': [46.4664, 10.3759],
    'ANTERSELVA': [46.8584, 12.1332],
    'VAL DI FIEMME': [46.2837, 11.5342],
    'VERONA': [45.4384, 10.9916],
    'BOLZANO': [46.4983, 11.3548],
    'TRENTO': [46.0678, 11.1211]
};

// 计费常量
export const BASE_DAY_RATE = 900;
export const FREE_KM = 200;
export const KM_RATE = 2.5;
export const FREE_HOURS = 10;
export const OT_RATE = 80;
