import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private apiUrl = `${environment.apiUrl}/admin`;

  constructor(private http: HttpClient) {}

  getMetrics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/metrics`);
  }

  getMatrixUrl(filename: string): string {
    return `${this.apiUrl}/matrix/${filename}`;
  }

  getActiveModels(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/active-models`);
  }

  setActiveModel(disease: string, model_name: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/active-models`, { disease, model_name });
  }
}
