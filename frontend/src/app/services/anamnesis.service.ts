import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface AnamnesisPredictionResult {
  risk_level: string;
  confidence: number;
  description: string;
  model_used?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AnamnesisService {
  private apiUrl = `${environment.apiUrl}/api/v1/anamnesis`;

  constructor(private http: HttpClient) {}

  analyze(formData: FormData): Observable<AnamnesisPredictionResult> {
    return this.http.post<AnamnesisPredictionResult>(`${this.apiUrl}/analyze`, formData);
  }
}
