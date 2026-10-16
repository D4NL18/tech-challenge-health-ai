import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface LocationPoint {
  id: string;
  name: string;
  lat: floatNumber;
  lon: floatNumber;
}

export type floatNumber = number;

export interface DeliveryPoint extends LocationPoint {
  demand: number;
  priority: string;
  critical_medication: boolean;
  assigned_vehicle?: number | null;
}

export interface FleetConfig {
  num_vehicles: number;
  capacity_per_vehicle: number;
  max_distance_km: number;
}

export interface GAParameters {
  population_size: number;
  generations: number;
  mutation_rate: number;
}

export interface OptimizeRoutesPayload {
  depot: LocationPoint;
  deliveries: DeliveryPoint[];
  fleet: FleetConfig;
  ga_params: GAParameters;
}

export interface StopInfo {
  step: number;
  name: string;
  lat: number;
  lon: number;
  action: string;
  critical: boolean;
  priority?: string;
  demand: number;
  assigned_vehicle?: number | null;
  arrival_time_minutes?: number;
}

export interface VehicleRouteResponse {
  vehicle_id: number;
  stops: StopInfo[];
  route_time_minutes: number;
  route_distance_km: number;
  geojson_geometry: any;
}

export interface OptimizeRoutesResponse {
  success: boolean;
  summary: {
    total_time_minutes: number;
    total_distance_km: number;
    average_time_minutes?: number;
    average_distance_km?: number;
    vehicles_used: number;
    total_deliveries: number;
    urgency_makespan_minutes?: number;
    elapsed_seconds: number;
  };
  routes: VehicleRouteResponse[];
  fitness_history: number[];
}

@Injectable({
  providedIn: 'root'
})
export class RoutesService {
  private apiUrl = `${environment.apiUrl}/api/v1/routes`;

  constructor(private http: HttpClient) {}

  getDemoScenario(city: string = 'salvador'): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/demo-scenario?city=${city}`);
  }

  geocodeAddress(query: string): Observable<Array<{ name: string; display_name: string; lat: number; lon: number; type: string }>> {
    return this.http.get<Array<{ name: string; display_name: string; lat: number; lon: number; type: string }>>(
      `${this.apiUrl}/geocode?q=${encodeURIComponent(query)}`
    );
  }

  optimizeRoutes(payload: OptimizeRoutesPayload): Observable<OptimizeRoutesResponse> {
    return this.http.post<OptimizeRoutesResponse>(`${this.apiUrl}/optimize`, payload);
  }

  getDriverInstructions(payload: {
    vehicle_id: number;
    stops: StopInfo[];
    total_time_min: number;
    total_distance_km: number;
  }): Observable<{ instructions: string }> {
    return this.http.post<{ instructions: string }>(`${this.apiUrl}/instructions`, payload);
  }

  getEfficiencyReport(payload: {
    summary: any;
    routes: VehicleRouteResponse[];
  }): Observable<{ report: string }> {
    return this.http.post<{ report: string }>(`${this.apiUrl}/report`, payload);
  }

  chatRoutes(payload: { question: string; context: any }): Observable<{ answer: string }> {
    return this.http.post<{ answer: string }>(`${this.apiUrl}/chat`, payload);
  }
}
