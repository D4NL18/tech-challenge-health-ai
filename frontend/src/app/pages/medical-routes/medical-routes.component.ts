import { Component, OnInit, AfterViewInit, OnDestroy, signal, NgZone, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { 
  RoutesService, 
  OptimizeRoutesPayload, 
  OptimizeRoutesResponse, 
  VehicleRouteResponse, 
  LocationPoint, 
  DeliveryPoint 
} from '../../services/routes.service';

declare let L: any;

export interface FavoritePoint {
  id: string;
  name: string;
  lat: number;
  lon: number;
  critical: boolean;
}

@Component({
  selector: 'app-medical-routes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './medical-routes.component.html',
  styleUrl: './medical-routes.component.scss'
})
export class MedicalRoutesComponent implements OnInit, AfterViewInit, OnDestroy {
  // Estado reativo da interface
  isLoading = signal<boolean>(false);
  isGeneratingLLM = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  toastMessage = signal<string | null>(null);

  // Navegação da Coluna de Controle / Resultados
  activeSidebarTab = signal<'points' | 'results'>('points');
  activeTab = signal<'itinerary' | 'instructions' | 'report' | 'chat'>('itinerary');

  // Base Central (Hub de Partida e Retorno): Se não tiver salva no localStorage, inicia como null (sem nada marcado)
  depot = signal<LocationPoint | null>(null);

  // O MAPA COMEÇA ZERADO: Lista de entregas inicialmente vazia
  deliveries: DeliveryPoint[] = [];

  // Sistema de Favoritos persistido no LocalStorage
  favorites = signal<FavoritePoint[]>([]);

  // Busca e Autocomplete de Endereços com Nominatim OpenStreetMap
  searchQuery: string = '';
  searchResults = signal<Array<{ name: string; display_name: string; lat: number; lon: number; type: string }>>([]);
  isSearchingAddress = signal<boolean>(false);
  showSearchDropdown = signal<boolean>(false);
  selectedSearchItem: any = null;
  private searchDebounceTimer: any = null;

  // Parâmetros de Frota e Algoritmo Genético VRP
  numVehicles: number = 2;
  capacityPerVehicle: number = 110.0;
  maxDistanceKm: number = 100.0;
  populationSize: number = 40;
  generations: number = 25;
  mutationRate: number = 0.20;

  // MODAL DE CONFIGURAÇÃO DE PARÂMETROS DO AG & FROTA
  showConfigModal = signal<boolean>(false);
  private isConfigBackdropMouseDown = false;

  // MODAL AO CLICAR NO MAPA (Nome, Urgência Clínica e Base)
  showPointModal = signal<boolean>(false);
  modalPointType: 'delivery' | 'depot' = 'delivery';
  modalPointName: string = '';
  modalPointLat: number = -12.9800;
  modalPointLon: number = -38.5000;
  modalPointPriority: 'CRITICAL' | 'HIGH' | 'REGULAR' = 'REGULAR';
  modalPointCritical: boolean = false;
  modalPointAssignedVehicle: number | null = null;
  modalPointSaveFavorite: boolean = false;
  editingPointIndex: number | null = null; // null = novo ponto, número = edição de ponto existente

  // Resultados da Otimização
  optimizationResult: OptimizeRoutesResponse | null = null;
  selectedVehicleId: number = 1;
  filteredVehicleId = signal<number>(0); // 0 = Todas as Vans, 1 = Van 1, etc.
  driverInstructionsText = signal<string>('');
  efficiencyReportText = signal<string>('');

  getVehicleColor(vehicleId: number): string {
    return this.vehicleColors[(vehicleId - 1) % this.vehicleColors.length];
  }

  setNumVehicles(count: number): void {
    const newCount = Math.min(6, Math.max(1, count));
    if (this.numVehicles !== newCount) {
      this.numVehicles = newCount;
      if (this.optimizationResult && this.deliveries.length > 0) {
        this.runOptimization();
      }
    }
  }

  getVehicleOptions(): number[] {
    const list: number[] = [];
    for (let i = 1; i <= this.numVehicles; i++) {
      list.push(i);
    }
    return list;
  }

  filterByVehicle(vId: number): void {
    this.filteredVehicleId.set(vId);
    this.selectedVehicleId = vId > 0 ? vId : 1;
    if (this.optimizationResult) {
      if (vId === 0) {
        this.renderRoutesOnMap(this.optimizationResult.routes);
      } else {
        const filtered = this.optimizationResult.routes.filter((r) => r.vehicle_id === vId);
        this.renderRoutesOnMap(filtered);
      }
    }
  }

  getVisibleRoutes(): VehicleRouteResponse[] {
    if (!this.optimizationResult) return [];
    const fId = this.filteredVehicleId();
    if (fId === 0) {
      return this.optimizationResult.routes;
    }
    return this.optimizationResult.routes.filter((r) => r.vehicle_id === fId);
  }

  getAverageTimeMinutes(): number {
    if (!this.optimizationResult) return 0;
    if (this.optimizationResult.summary.average_time_minutes !== undefined) {
      return this.optimizationResult.summary.average_time_minutes;
    }
    const vans = this.optimizationResult.summary.vehicles_used || 1;
    return Number((this.optimizationResult.summary.total_time_minutes / vans).toFixed(1));
  }

  getAverageDistanceKm(): number {
    if (!this.optimizationResult) return 0;
    if (this.optimizationResult.summary.average_distance_km !== undefined) {
      return this.optimizationResult.summary.average_distance_km;
    }
    const vans = this.optimizationResult.summary.vehicles_used || 1;
    return Number((this.optimizationResult.summary.total_distance_km / vans).toFixed(1));
  }

  // Chat Conversacional RAG com a IA
  chatQuestion: string = '';
  chatMessages = signal<Array<{ sender: 'user' | 'ai'; text: string }>>([
    {
      sender: 'ai',
      text: 'Olá! Sou o assistente de logística hospitalar em Salvador-BA. Ao otimizar as rotas, tire suas dúvidas sobre tempos de percurso, abastecimento de UPAs e transporte de medicamentos críticos.'
    }
  ]);

  // Leaflet Map & Camadas Gráficas
  private map: any = null;
  private markersLayer: any = null;
  private routesLayer: any = null;
  private previewMarker: any = null;

  // Paleta de cores vibrantes para distinguir cada van da frota
  private vehicleColors = ['#FF4B72', '#7B61FF', '#10B981', '#F59E0B', '#06B6D4', '#EC4899'];

  constructor(
    private routesService: RoutesService,
    private ngZone: NgZone,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadSavedDepot();
    this.loadSavedFavorites();
  }

  ngAfterViewInit(): void {
    this.initMap();
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }

  /**
   * Carrega a Base Central do LocalStorage caso o usuário tenha salvo anteriormente.
   * Se não houver nada salvo, o mapa inicia sem nenhuma base (depot = null).
   */
  private loadSavedDepot(): void {
    try {
      const saved = localStorage.getItem('healthai_custom_depot');
      if (saved) {
        this.depot.set(JSON.parse(saved));
      } else {
        this.depot.set(null);
      }
    } catch {
      this.depot.set(null);
    }
  }

  /**
   * Carrega a lista de locais favoritos do LocalStorage
   */
  private loadSavedFavorites(): void {
    try {
      const saved = localStorage.getItem('healthai_favorite_points');
      if (saved) {
        this.favorites.set(JSON.parse(saved));
      } else {
        this.favorites.set([]);
      }
    } catch {
      this.favorites.set([]);
    }
  }

  private saveFavoritesToStorage(): void {
    localStorage.setItem('healthai_favorite_points', JSON.stringify(this.favorites()));
  }

  /**
   * Inicializa o mapa com Leaflet, centralizado por padrão em Salvador-BA
   */
  private initMap(): void {
    if (typeof L === 'undefined') {
      console.warn('Leaflet ainda não carregado no DOM.');
      return;
    }

    this.map = L.map('map-container', {
      center: [-12.9777, -38.5016],
      zoom: 13,
      zoomControl: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | OSRM Engine',
      maxZoom: 19
    }).addTo(this.map);

    this.markersLayer = L.layerGroup().addTo(this.map);
    this.routesLayer = L.layerGroup().addTo(this.map);

    // Escuta cliques no mapa EXECUTANDO NA NGZONE para abrir o modal de forma garantida
    this.map.on('click', (e: any) => {
      this.ngZone.run(() => {
        this.openModalForCoordinates(e.latlng.lat, e.latlng.lng);
      });
    });

    this.updateMapMarkers();

    setTimeout(() => {
      if (this.map) {
        this.map.invalidateSize();
      }
    }, 250);
  }

  onSearchInput(): void {
    if (this.searchDebounceTimer) {
      clearTimeout(this.searchDebounceTimer);
    }

    const query = this.searchQuery.trim();
    if (query.length < 2) {
      this.searchResults.set([]);
      // Mantém o dropdown aberto se houver favoritos para busca rápida
      this.showSearchDropdown.set(this.favorites().length > 0);
      return;
    }

    this.searchDebounceTimer = setTimeout(() => {
      this.executeAddressSearch(query);
    }, 350);
  }

  executeAddressSearch(query?: string): void {
    const q = query || this.searchQuery.trim();
    if (!q || q.length < 2) return;

    this.isSearchingAddress.set(true);
    this.routesService.geocodeAddress(q).subscribe({
      next: (results) => {
        this.ngZone.run(() => {
          this.searchResults.set(results);
          this.showSearchDropdown.set(true);
          this.isSearchingAddress.set(false);
          this.cdr.detectChanges();
        });
      },
      error: (err) => {
        console.error('Erro no geocoding:', err);
        this.isSearchingAddress.set(false);
      }
    });
  }

  selectAddressOption(item: any): void {
    this.selectedSearchItem = item;
    this.showSearchDropdown.set(false);
    this.searchQuery = item.name;

    if (!this.map || typeof L === 'undefined') return;

    if (this.previewMarker) {
      this.map.removeLayer(this.previewMarker);
    }

    this.map.flyTo([item.lat, item.lon], 16, {
      duration: 1.6,
      easeLinearity: 0.25
    });

    const previewIcon = L.divIcon({
      className: 'preview-search-marker',
      html: `<div style="background: #7B61FF; color: white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 18px; box-shadow: 0 0 16px rgba(123,97,255,0.7); border: 2.5px solid #fff; animation: pulseGlow 1.5s infinite;">📍</div>`,
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });

    this.previewMarker = L.marker([item.lat, item.lon], { icon: previewIcon })
      .addTo(this.map)
      .bindPopup(`
        <div style="min-width: 220px; padding: 6px;">
          <strong style="font-size: 14px; color: #1e293b; display: block; margin-bottom: 4px;">${item.name}</strong>
          <p style="font-size: 12px; color: #64748b; margin: 0 0 10px 0; line-height: 1.4;">${item.display_name}</p>
          <button id="btn-open-modal-preview" style="background: linear-gradient(135deg, #FF4B72, #7B61FF); color: white; border: none; padding: 7px 12px; border-radius: 6px; font-weight: bold; font-size: 12px; cursor: pointer; width: 100%;">
            ⚙️ Configurar Parada ou Base
          </button>
        </div>
      `)
      .openPopup();

    setTimeout(() => {
      const btn = document.getElementById('btn-open-modal-preview');
      if (btn) {
        btn.onclick = () => {
          this.ngZone.run(() => {
            this.openModalForCoordinates(item.lat, item.lon, item.name);
          });
        };
      }
    }, 300);

    this.showToastNotification(`🎯 Mapa centralizado em: ${item.name}. Clique no ponto para configurar.`);
  }

  onSearchFocus(): void {
    if (this.favorites().length > 0 || this.searchResults().length > 0) {
      this.showSearchDropdown.set(true);
    }
  }

  getFilteredFavorites(): FavoritePoint[] {
    const q = this.searchQuery.trim().toLowerCase();
    if (!q) return this.favorites();
    return this.favorites().filter(f => f.name.toLowerCase().includes(q));
  }

  /**
   * Abre o Modal ao clicar no mapa ou ao selecionar da busca
   */
  openModalForCoordinates(lat: number, lon: number, suggestedName?: string): void {
    this.editingPointIndex = null;
    this.showSearchDropdown.set(false);
    // Se ainda não houver Base Central definida, sugere que este primeiro ponto seja a Base
    this.modalPointType = !this.depot() ? 'depot' : 'delivery';
    const nextIdx = this.deliveries.length + 1;
    this.modalPointName = suggestedName || (this.modalPointType === 'depot' ? 'Base Central Salvador' : `Ponto de Parada #${nextIdx}`);
    this.modalPointLat = parseFloat(lat.toFixed(5));
    this.modalPointLon = parseFloat(lon.toFixed(5));
    this.modalPointPriority = 'REGULAR';
    this.modalPointCritical = false;
    this.modalPointAssignedVehicle = null;
    this.modalPointSaveFavorite = this.isFavorite(this.modalPointLat, this.modalPointLon);
    this.showPointModal.set(true);
    this.cdr.detectChanges();
  }

  /**
   * Abre o Modal para editar a Base Central salva
   */
  openEditDepotModal(): void {
    const curDepot = this.depot();
    if (!curDepot) return;
    this.editingPointIndex = -1; // -1 indica edição da Base Central
    this.modalPointType = 'depot';
    this.modalPointName = curDepot.name;
    this.modalPointLat = curDepot.lat;
    this.modalPointLon = curDepot.lon;
    this.modalPointPriority = 'REGULAR';
    this.modalPointCritical = false;
    this.modalPointAssignedVehicle = null;
    this.modalPointSaveFavorite = this.isFavorite(curDepot.lat, curDepot.lon);
    this.showPointModal.set(true);
    this.cdr.detectChanges();
  }

  /**
   * Abre o Modal para editar um ponto existente da lista
   */
  openEditPointModal(index: number): void {
    this.editingPointIndex = index;
    this.modalPointType = 'delivery';
    const p = this.deliveries[index];
    this.modalPointName = p.name;
    this.modalPointLat = p.lat;
    this.modalPointLon = p.lon;
    const rawPrio = (p.priority || (p.critical_medication ? 'CRITICAL' : 'REGULAR')).toUpperCase();
    this.modalPointPriority = (rawPrio === 'CRITICAL' || rawPrio === 'HIGH') ? rawPrio as 'CRITICAL' | 'HIGH' : 'REGULAR';
    this.modalPointCritical = (this.modalPointPriority === 'CRITICAL');
    this.modalPointAssignedVehicle = p.assigned_vehicle ?? null;
    this.modalPointSaveFavorite = this.isFavorite(p.lat, p.lon);
    this.showPointModal.set(true);
    this.cdr.detectChanges();
  }

  closePointModal(): void {
    this.showPointModal.set(false);
    this.editingPointIndex = null;
    this.isBackdropMouseDown = false;
    this.cdr.detectChanges();
  }

  private isBackdropMouseDown = false;

  onBackdropMouseDown(event: MouseEvent): void {
    this.isBackdropMouseDown = (event.target === event.currentTarget);
  }

  onBackdropMouseUp(event: MouseEvent): void {
    if (this.isBackdropMouseDown && event.target === event.currentTarget) {
      this.closePointModal();
    }
    this.isBackdropMouseDown = false;
  }

  // --- CONTROLE DO MODAL DE CONFIGURAÇÃO DE PARÂMETROS DO AG ---
  openConfigModal(): void {
    this.showConfigModal.set(true);
    this.cdr.detectChanges();
  }

  closeConfigModal(): void {
    this.showConfigModal.set(false);
    this.isConfigBackdropMouseDown = false;
    this.cdr.detectChanges();
    if (this.optimizationResult && this.deliveries.length > 0) {
      this.runOptimization();
    }
  }

  onConfigBackdropMouseDown(event: MouseEvent): void {
    this.isConfigBackdropMouseDown = (event.target === event.currentTarget);
  }

  onConfigBackdropMouseUp(event: MouseEvent): void {
    if (this.isConfigBackdropMouseDown && event.target === event.currentTarget) {
      this.closeConfigModal();
    }
    this.isConfigBackdropMouseDown = false;
  }

  resetConfigDefaults(): void {
    this.numVehicles = 2;
    this.maxDistanceKm = 100.0;
    this.populationSize = 40;
    this.generations = 25;
    this.mutationRate = 0.20;
    this.showToastNotification('⚙️ Parâmetros redefinidos para os valores padrão.');
    this.cdr.detectChanges();
  }

  /**
   * Confirma e salva o ponto (novo ou editado, como Parada ou como Base)
   */
  confirmSavePoint(): void {
    if (!this.modalPointName.trim()) {
      this.modalPointName = this.modalPointType === 'depot' 
        ? 'Base Central Salvador' 
        : `Ponto #${this.deliveries.length + 1}`;
    }

    const trimmedName = this.modalPointName.trim();

    // 1. Tratamento para BASE CENTRAL
    if (this.modalPointType === 'depot' || this.editingPointIndex === -1) {
      this.modalPointSaveFavorite = false;
      const newDepot: LocationPoint = {
        id: this.depot()?.id || `depot-${Date.now()}`,
        name: trimmedName,
        lat: this.modalPointLat,
        lon: this.modalPointLon
      };
      this.depot.set(newDepot);
      localStorage.setItem('healthai_custom_depot', JSON.stringify(newDepot));
      this.showToastNotification(`🏢 "${newDepot.name}" salva como Base Central padrão!`);
    } else {
      // 2. Tratamento para PARADA DE ENTREGA
      const assignedVehicle = this.modalPointAssignedVehicle ? Number(this.modalPointAssignedVehicle) : null;
      const prio = this.modalPointPriority;
      const isCrit = (prio === 'CRITICAL');

      if (this.editingPointIndex !== null && this.editingPointIndex >= 0) {
        const p = this.deliveries[this.editingPointIndex];
        p.name = trimmedName;
        p.lat = this.modalPointLat;
        p.lon = this.modalPointLon;
        p.critical_medication = isCrit;
        p.priority = prio;
        p.assigned_vehicle = assignedVehicle;
        this.showToastNotification(`✏️ "${p.name}" atualizado.`);
      } else {
        const newPoint: DeliveryPoint = {
          id: `del-${Date.now()}-${this.deliveries.length + 1}`,
          name: trimmedName,
          lat: this.modalPointLat,
          lon: this.modalPointLon,
          demand: 10.0,
          priority: prio,
          critical_medication: isCrit,
          assigned_vehicle: assignedVehicle
        };
        this.deliveries.push(newPoint);
        this.showToastNotification(`📍 "${newPoint.name}" adicionado à rota!`);
      }
    }

    // Gerenciamento de Favorito
    if (this.modalPointSaveFavorite) {
      this.addFavorite(trimmedName, this.modalPointLat, this.modalPointLon, this.modalPointCritical);
    } else if (this.isFavorite(this.modalPointLat, this.modalPointLon)) {
      this.removeFavoriteByCoords(this.modalPointLat, this.modalPointLon);
    }

    if (this.previewMarker && this.map) {
      this.map.removeLayer(this.previewMarker);
      this.previewMarker = null;
    }

    this.clearCalculatedRoutes();
    this.updateMapMarkers();
    this.closePointModal();
    this.activeSidebarTab.set('points');
  }

  /**
   * Define um ponto existente da lista como a Base Central
   */
  promoteToDepot(index: number): void {
    const point = this.deliveries.splice(index, 1)[0];
    const newDepot: LocationPoint = {
      id: `depot-${Date.now()}`,
      name: point.name,
      lat: point.lat,
      lon: point.lon
    };
    this.depot.set(newDepot);
    localStorage.setItem('healthai_custom_depot', JSON.stringify(newDepot));
    this.clearCalculatedRoutes();
    this.updateMapMarkers();
    this.showToastNotification(`🏢 "${newDepot.name}" agora é a Base Central de Expedição!`);
  }

  /**
   * Limpa a Base Central customizada do LocalStorage
   */
  clearCustomDepot(): void {
    this.depot.set(null);
    localStorage.removeItem('healthai_custom_depot');
    this.clearCalculatedRoutes();
    this.updateMapMarkers();
    this.showToastNotification('🧹 Base Central removida. Defina um novo ponto como Base.');
  }

  // --- GERENCIAMENTO DE FAVORITOS ---
  isFavorite(lat: number, lon: number): boolean {
    return this.favorites().some(
      f => Math.abs(f.lat - lat) < 0.0001 && Math.abs(f.lon - lon) < 0.0001
    );
  }

  toggleFavorite(point: { name: string; lat: number; lon: number; critical_medication?: boolean; critical?: boolean }): void {
    const isCrit = point.critical_medication || point.critical || false;
    const existingIdx = this.favorites().findIndex(
      f => Math.abs(f.lat - point.lat) < 0.0001 && Math.abs(f.lon - point.lon) < 0.0001
    );

    if (existingIdx >= 0) {
      const updated = [...this.favorites()];
      updated.splice(existingIdx, 1);
      this.favorites.set(updated);
      this.saveFavoritesToStorage();
      this.showToastNotification(`⭐ "${point.name}" removido dos favoritos.`);
    } else {
      this.addFavorite(point.name, point.lat, point.lon, isCrit);
      this.showToastNotification(`⭐ "${point.name}" adicionado aos favoritos!`);
    }
  }

  addFavorite(name: string, lat: number, lon: number, critical: boolean): void {
    if (!this.isFavorite(lat, lon)) {
      const newFav: FavoritePoint = {
        id: `fav-${Date.now()}`,
        name,
        lat,
        lon,
        critical
      };
      this.favorites.set([...this.favorites(), newFav]);
      this.saveFavoritesToStorage();
    }
  }

  removeFavoriteByCoords(lat: number, lon: number): void {
    const updated = this.favorites().filter(
      f => !(Math.abs(f.lat - lat) < 0.0001 && Math.abs(f.lon - lon) < 0.0001)
    );
    this.favorites.set(updated);
    this.saveFavoritesToStorage();
  }

  selectFavorite(fav: FavoritePoint): void {
    this.showSearchDropdown.set(false);
    this.searchQuery = fav.name;
    if (this.map) {
      this.map.flyTo([fav.lat, fav.lon], 16, { duration: 1.5 });
    }
    this.openModalForCoordinates(fav.lat, fav.lon, fav.name);
    this.modalPointCritical = fav.critical;
    this.modalPointSaveFavorite = true;
  }

  removeFavoriteById(favId: string, event: Event): void {
    event.stopPropagation();
    const updated = this.favorites().filter(f => f.id !== favId);
    this.favorites.set(updated);
    this.saveFavoritesToStorage();
    this.showToastNotification('⭐ Favorito excluído.');
  }

  removeDelivery(index: number): void {
    const removed = this.deliveries.splice(index, 1);
    this.clearCalculatedRoutes();
    this.updateMapMarkers();
    if (removed.length > 0) {
      this.showToastNotification(`🗑️ "${removed[0].name}" removido.`);
    }
  }

  toggleCritical(index: number): void {
    const point = this.deliveries[index];
    point.critical_medication = !point.critical_medication;
    point.priority = point.critical_medication ? 'HIGH' : 'REGULAR';
    this.clearCalculatedRoutes();
    this.updateMapMarkers();
    this.showToastNotification(
      `Status de "${point.name}": ${point.critical_medication ? '🚨 Crítico (Refrigerado)' : '📦 Regular'}`
    );
  }

  onAssignedVehicleChange(index: number, newVehicle: any): void {
    const point = this.deliveries[index];
    const val = newVehicle === '' || newVehicle === null ? null : Number(newVehicle);
    point.assigned_vehicle = val;
    this.clearCalculatedRoutes();
    this.updateMapMarkers();
    if (val) {
      this.showToastNotification(`🚐 "${point.name}" vinculado exclusivamente à Van ${val}.`);
    } else {
      this.showToastNotification(`⚡ "${point.name}" com motorista definido automaticamente.`);
    }
  }

  cyclePriority(index: number): void {
    const point = this.deliveries[index];
    const prio = (point.priority || (point.critical_medication ? 'CRITICAL' : 'REGULAR')).toUpperCase();
    if (prio === 'REGULAR') {
      point.priority = 'HIGH';
      point.critical_medication = false;
      this.showToastNotification(`⚡ "${point.name}" definida como Alta Prioridade.`);
    } else if (prio === 'HIGH') {
      point.priority = 'CRITICAL';
      point.critical_medication = true;
      this.showToastNotification(`🚨 "${point.name}" definida como Urgência Crítica.`);
    } else {
      point.priority = 'REGULAR';
      point.critical_medication = false;
      this.showToastNotification(`📦 "${point.name}" definida como Regular.`);
    }
    this.clearCalculatedRoutes();
    this.updateMapMarkers();
  }

  setModalPriority(priority: 'CRITICAL' | 'HIGH' | 'REGULAR'): void {
    this.modalPointPriority = priority;
    this.modalPointCritical = (priority === 'CRITICAL');
  }

  clearAllPoints(): void {
    this.deliveries = [];
    this.clearCalculatedRoutes();
    if (this.previewMarker && this.map) {
      this.map.removeLayer(this.previewMarker);
      this.previewMarker = null;
    }
    this.updateMapMarkers();
    this.activeSidebarTab.set('points');
    this.showToastNotification('🧹 Paradas limpas. A Base Central foi mantida.');
  }

  loadDemoScenario(city: string = 'salvador'): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.routesService.getDemoScenario(city).subscribe({
      next: (scenario) => {
        this.depot.set(scenario.depot);
        localStorage.setItem('healthai_custom_depot', JSON.stringify(scenario.depot));
        this.deliveries = scenario.deliveries;
        this.numVehicles = scenario.fleet.num_vehicles;
        this.capacityPerVehicle = scenario.fleet.capacity_per_vehicle;
        this.maxDistanceKm = scenario.fleet.max_distance_km;
        this.populationSize = scenario.ga_params.population_size;
        this.generations = scenario.ga_params.generations;
        this.mutationRate = scenario.ga_params.mutation_rate;
        this.clearCalculatedRoutes();
        this.isLoading.set(false);
        this.updateMapMarkers();
        this.activeSidebarTab.set('points');
        this.fitMapToMarkers();
        this.showToastNotification(
          city === 'salvador' 
            ? '✅ Cenário de Salvador-BA carregado com Base e 10 paradas!'
            : '✅ Cenário de São Paulo carregado com Base e 10 paradas!'
        );
      },
      error: (err) => {
        console.error('Erro ao carregar cenário demo:', err);
        this.errorMessage.set('Não foi possível carregar o cenário demo do servidor.');
        this.isLoading.set(false);
      }
    });
  }

  private clearCalculatedRoutes(): void {
    this.optimizationResult = null;
    if (this.routesLayer) {
      this.routesLayer.clearLayers();
    }
    this.driverInstructionsText.set('');
    this.efficiencyReportText.set('');
  }

  private updateMapMarkers(): void {
    if (!this.map || !this.markersLayer || typeof L === 'undefined') return;

    this.markersLayer.clearLayers();

    // 1. Hub / Base Central (se existir salva)
    const currentDepot = this.depot();
    if (currentDepot) {
      const hubIcon = L.divIcon({
        className: 'custom-hub-marker',
        html: `<div style="background: #0F172A; color: white; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 0 18px rgba(15,23,42,0.7); border: 2.5px solid #fff;">🏢</div>`,
        iconSize: [38, 38],
        iconAnchor: [19, 19]
      });

      L.marker([currentDepot.lat, currentDepot.lon], { icon: hubIcon })
        .addTo(this.markersLayer)
        .bindPopup(`
          <div style="min-width: 190px; padding: 4px;">
            <strong style="color: #0F172A; font-size: 14px;">${currentDepot.name}</strong><br>
            <span style="font-size: 11px; background: #f1f5f9; color: #0F172A; padding: 2px 6px; border-radius: 4px; font-weight: bold; border: 1px solid #cbd5e1;">BASE CENTRAL (PONTO DE PARTIDA)</span>
            <div style="margin-top: 6px; font-size: 11px; color: #64748b;">Coord: ${currentDepot.lat.toFixed(4)}, ${currentDepot.lon.toFixed(4)}</div>
          </div>
        `);
    }

    // 2. Marcadores das paradas cadastradas
    this.deliveries.forEach((d, idx) => {
      const prio = (d.priority || (d.critical_medication ? 'CRITICAL' : 'REGULAR')).toUpperCase();
      let bgColor = '#2563EB'; // REGULAR (Blue)
      let priorityLabel = '<span style="color: #2563EB; font-weight: 600;">📦 Regular (Insumos de Rotina)</span>';

      if (prio === 'CRITICAL' || d.critical_medication) {
        bgColor = '#E11D48'; // Rose / Red
        priorityLabel = '<span style="color: #E11D48; font-weight: 700;">🚨 Urgência Crítica (Cadeia de Frio / Sangue)</span>';
      } else if (prio === 'HIGH') {
        bgColor = '#F59E0B'; // Amber / Orange
        priorityLabel = '<span style="color: #D97706; font-weight: 700;">⚡ Alta Prioridade (UTI / Antibióticos)</span>';
      }

      const badges: string[] = [];
      if (d.assigned_vehicle) {
        badges.push(`V${d.assigned_vehicle}`);
      }
      if (prio === 'CRITICAL') {
        badges.push('🚨');
      } else if (prio === 'HIGH') {
        badges.push('⚡');
      }

      const badgeHtml = badges.length > 0 
        ? `<span style="position: absolute; top: -8px; right: -8px; background: #7B61FF; color: white; border-radius: 8px; font-size: 8px; padding: 1px 4px; display: flex; align-items: center; justify-content: center; border: 1px solid white; font-weight: bold; white-space: nowrap; box-shadow: 0 1px 4px rgba(0,0,0,0.3);">${badges.join(' ')}</span>`
        : '';

      const delivIcon = L.divIcon({
        className: 'custom-deliv-marker',
        html: `
          <div style="position: relative; background: ${bgColor}; color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; box-shadow: 0 0 12px ${bgColor}99; border: 2px solid #fff;">
            ${idx + 1}
            ${badgeHtml}
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const vehicleLabel = d.assigned_vehicle 
        ? `<div style="margin-top: 4px; color: #7B61FF; font-weight: bold; font-size: 12px;">🚐 Van Vinculada: Van ${d.assigned_vehicle}</div>`
        : `<div style="margin-top: 4px; color: #64748b; font-size: 12px;">⚡ Motorista: Automático (IA)</div>`;

      const popupContent = `
        <div style="min-width: 190px; padding: 4px;">
          <strong style="font-size: 14px; display: block; margin-bottom: 4px;">${d.name}</strong>
          <div>${priorityLabel}</div>
          ${vehicleLabel}
          <div style="font-size: 11px; color: #888; margin-top: 4px;">Coord: ${d.lat.toFixed(4)}, ${d.lon.toFixed(4)}</div>
        </div>
      `;

      L.marker([d.lat, d.lon], { icon: delivIcon })
        .addTo(this.markersLayer)
        .bindPopup(popupContent);
    });
  }

  private fitMapToMarkers(): void {
    if (!this.map || typeof L === 'undefined') return;
    const bounds = L.latLngBounds([]);
    const curDepot = this.depot();
    if (curDepot) {
      bounds.extend([curDepot.lat, curDepot.lon]);
    }
    this.deliveries.forEach(d => bounds.extend([d.lat, d.lon]));
    if (bounds.isValid()) {
      this.map.fitBounds(bounds, { padding: [50, 50] });
    }
  }

  runOptimization(): void {
    const curDepot = this.depot();
    if (!curDepot) {
      this.errorMessage.set('É necessário definir uma Base Central antes de otimizar rotas. Clique no mapa e marque a opção "🏢 Base Central de Expedição".');
      return;
    }

    if (this.deliveries.length === 0) {
      this.errorMessage.set('Adicione ao menos uma parada de entrega no mapa ou carregue o cenário de demonstração.');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const payload: OptimizeRoutesPayload = {
      depot: curDepot,
      deliveries: this.deliveries,
      fleet: {
        num_vehicles: this.numVehicles,
        capacity_per_vehicle: this.capacityPerVehicle,
        max_distance_km: this.maxDistanceKm
      },
      ga_params: {
        population_size: this.populationSize,
        generations: this.generations,
        mutation_rate: this.mutationRate
      }
    };

    this.routesService.optimizeRoutes(payload).subscribe({
      next: (res) => {
        this.optimizationResult = res;
        this.isLoading.set(false);
        this.activeSidebarTab.set('results');
        this.activeTab.set('itinerary');
        this.filteredVehicleId.set(0);
        this.renderRoutesOnMap(res.routes);
        this.showToastNotification('🎉 Otimização equilibrada concluída com sucesso!');
      },
      error: (err) => {
        console.error('Erro na otimização:', err);
        this.errorMessage.set(
          err.error?.detail || 'Falha ao otimizar rotas com o OSRM. Verifique a conexão com o servidor.'
        );
        this.isLoading.set(false);
      }
    });
  }

  private renderRoutesOnMap(routes: VehicleRouteResponse[]): void {
    if (!this.map || !this.routesLayer || typeof L === 'undefined') return;

    this.routesLayer.clearLayers();
    const bounds = L.latLngBounds([]);
    const curDepot = this.depot();
    if (curDepot) {
      bounds.extend([curDepot.lat, curDepot.lon]);
    }

    routes.forEach((route) => {
      const color = this.getVehicleColor(route.vehicle_id);

      if (route.geojson_geometry && route.geojson_geometry.coordinates) {
        const geoLayer = L.geoJSON(route.geojson_geometry, {
          style: {
            color: color,
            weight: 6,
            opacity: 0.88,
            dashArray: route.vehicle_id % 2 === 0 ? '7, 7' : undefined
          }
        }).addTo(this.routesLayer);

        geoLayer.bindPopup(
          `<b>Van ${route.vehicle_id}</b><br>Tempo Viário: ${route.route_time_minutes} min<br>Distância: ${route.route_distance_km} km`
        );
      }

      route.stops.forEach((stop) => {
        if (stop.lat && stop.lon) {
          bounds.extend([stop.lat, stop.lon]);
          if (stop.action === 'DELIVERY') {
            const stepIcon = L.divIcon({
              className: 'step-badge',
              html: `<span style="background: ${color}; color: white; padding: 2px 7px; border-radius: 12px; font-weight: 800; font-size: 11px; border: 1.5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.35);">#${stop.step}</span>`,
              iconSize: [28, 18],
              iconAnchor: [-10, 8]
            });
            L.marker([stop.lat, stop.lon], { icon: stepIcon }).addTo(this.routesLayer);
          }
        }
      });
    });

    if (bounds.isValid()) {
      this.map.fitBounds(bounds, { padding: [50, 50] });
    }
  }

  selectVehicle(vId: number): void {
    this.selectedVehicleId = vId;
    this.generateDriverInstructionsForVehicle(vId);
  }

  generateDriverInstructionsForVehicle(vId: number): void {
    if (!this.optimizationResult) return;
    const vRoute = this.optimizationResult.routes.find((r) => r.vehicle_id === vId);
    if (!vRoute) return;

    this.isGeneratingLLM.set(true);
    this.routesService.getDriverInstructions({
      vehicle_id: vRoute.vehicle_id,
      stops: vRoute.stops,
      total_time_min: vRoute.route_time_minutes,
      total_distance_km: vRoute.route_distance_km
    }).subscribe({
      next: (res) => {
        this.driverInstructionsText.set(res.instructions);
        this.isGeneratingLLM.set(false);
      },
      error: () => this.isGeneratingLLM.set(false)
    });
  }

  generateEfficiencyReport(): void {
    if (!this.optimizationResult) return;
    this.isGeneratingLLM.set(true);
    this.routesService.getEfficiencyReport({
      summary: this.optimizationResult.summary,
      routes: this.optimizationResult.routes
    }).subscribe({
      next: (res) => {
        this.efficiencyReportText.set(res.report);
        this.isGeneratingLLM.set(false);
      },
      error: () => this.isGeneratingLLM.set(false)
    });
  }

  sendChatMessage(): void {
    if (!this.chatQuestion.trim()) return;

    const userMsg = this.chatQuestion.trim();
    this.chatQuestion = '';

    const currentMsgs = this.chatMessages();
    this.chatMessages.set([...currentMsgs, { sender: 'user', text: userMsg }]);

    this.isGeneratingLLM.set(true);
    this.routesService.chatRoutes({
      question: userMsg,
      context: {
        summary: this.optimizationResult?.summary || {},
        routes: this.optimizationResult?.routes || []
      }
    }).subscribe({
      next: (res) => {
        this.chatMessages.set([
          ...this.chatMessages(),
          { sender: 'ai', text: res.answer }
        ]);
        this.isGeneratingLLM.set(false);
      },
      error: () => {
        this.chatMessages.set([
          ...this.chatMessages(),
          { sender: 'ai', text: 'Não foi possível processar a resposta da IA no momento.' }
        ]);
        this.isGeneratingLLM.set(false);
      }
    });
  }

  private showToastNotification(msg: string): void {
    this.toastMessage.set(msg);
    setTimeout(() => {
      if (this.toastMessage() === msg) {
        this.toastMessage.set(null);
      }
    }, 4000);
  }

  getCriticalCount(): number {
    return this.deliveries.filter(d => (d.priority || '').toUpperCase() === 'CRITICAL' || d.critical_medication).length;
  }

  getHighCount(): number {
    return this.deliveries.filter(d => (d.priority || '').toUpperCase() === 'HIGH' && !d.critical_medication).length;
  }

  getRegularCount(): number {
    return this.deliveries.filter(d => {
      const p = (d.priority || '').toUpperCase();
      return (p === 'REGULAR' || !p) && !d.critical_medication;
    }).length;
  }

  getAssignedCount(): number {
    return this.deliveries.filter(d => d.assigned_vehicle && d.assigned_vehicle > 0).length;
  }
}
