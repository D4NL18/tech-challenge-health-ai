import { Routes } from '@angular/router';
import { AnamnesisComponent } from './pages/anamnesis/anamnesis.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { AdminLoginComponent } from './pages/admin-login/admin-login.component';
import { AdminDashboardComponent } from './pages/admin-dashboard/admin-dashboard.component';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', component: AnamnesisComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'admin/login', component: AdminLoginComponent },
  { path: 'admin/dashboard', component: AdminDashboardComponent, canActivate: [AuthGuard] },
  { path: 'admin', redirectTo: 'admin/dashboard', pathMatch: 'full' }
];
