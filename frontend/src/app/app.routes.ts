import { Routes } from '@angular/router';
import { AnamnesisComponent } from './pages/anamnesis/anamnesis.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';

export const routes: Routes = [
  { path: '', component: AnamnesisComponent },
  { path: 'dashboard', component: DashboardComponent }
];
