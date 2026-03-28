/**
 * Hello Smart Vehicle HUD Card
 *
 * A custom Lovelace card bundled with the Hello Smart integration.
 * Displays a top-down vehicle image with door, window, trunk, and hood
 * status icons overlaid at their physical positions.
 *
 * Uses HA's entity registry (hass.entities) for robust device-based
 * entity discovery — works regardless of device name or entity ID prefix.
 *
 * Usage:
 *   type: custom:hello-smart-vehicle-card
 *   entity: binary_sensor.<any_hello_smart_entity>   # any entity from the device
 *
 * Optional:
 *   image: /local/hello_smart/MYVIN_top.png          # override auto-detected image
 *   show_windows: true                                # show window overlays (default: true)
 *   show_locks: true                                  # show lock status row (default: true)
 */

const CARD_VERSION = "1.2.1";

/* eslint-disable no-console */
console.info(
  `%c HELLO-SMART-VEHICLE-CARD %c v${CARD_VERSION} `,
  "color: white; background: #0078D4; font-weight: bold; padding: 2px 6px; border-radius: 4px 0 0 4px;",
  "color: #0078D4; background: #E8E8E8; font-weight: bold; padding: 2px 6px; border-radius: 0 4px 4px 0;"
);

/**
 * Overlay element positions (percentage-based).
 * Keys are translation_key values from the integration's binary sensor descriptions.
 */
const DOOR_POSITIONS = {
  driver_door:      { left: 18, top: 38 },
  passenger_door:   { left: 82, top: 38 },
  rear_left_door:   { left: 18, top: 58 },
  rear_right_door:  { left: 82, top: 58 },
  trunk:            { left: 50, top: 92 },
  engine_hood:      { left: 50, top: 8 },
};

const WINDOW_POSITIONS = {
  driver_window:      { left: 25, top: 38 },
  passenger_window:   { left: 75, top: 38 },
  rear_left_window:   { left: 25, top: 58 },
  rear_right_window:  { left: 75, top: 58 },
  sunroof_open:       { left: 50, top: 48 },
};

const LOCK_KEYS = [
  "door_lock_driver",
  "door_lock_passenger",
  "door_lock_rear_left",
  "door_lock_rear_right",
  "trunk_locked",
];

const LOCK_LABELS = {
  door_lock_driver: "Driver",
  door_lock_passenger: "Passenger",
  door_lock_rear_left: "Rear L",
  door_lock_rear_right: "Rear R",
  trunk_locked: "Trunk",
};

class HelloSmartVehicleCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    // Map of translation_key → entity_id, built from device registry
    this._keyMap = {};
    this._deviceId = null;
    this._connected = false;
  }

  connectedCallback() {
    this._connected = true;
    // Re-render when attached to DOM — hass may have arrived before connection
    if (this._hass && this._config.entity) {
      try {
        this._buildDeviceEntityMap();
        this._render();
      } catch (err) {
        this._renderError("connectedCallback", err);
      }
    }
  }

  disconnectedCallback() {
    this._connected = false;
  }

  static getStubConfig(hass) {
    // Auto-pick the first hello_smart driver_door entity
    const entity = HelloSmartVehicleCard._autoDetectEntity(hass);
    return { entity: entity || "", show_windows: true, show_locks: true };
  }

  static _autoDetectEntity(hass) {
    if (!hass) return "";
    const reg = hass.entities || {};
    // Find hello_smart driver_door entities (one per vehicle)
    for (const [entityId, entry] of Object.entries(reg)) {
      const pl = entry.platform || entry.pl;
      const tk = entry.translation_key || entry.tk;
      if (pl === "hello_smart" && tk === "driver_door") return entityId;
    }
    // Fallback: scan states
    for (const entityId of Object.keys(hass.states || {})) {
      if (entityId.includes("driver_door") && entityId.startsWith("binary_sensor.")) return entityId;
    }
    return "";
  }

  setConfig(config) {
    this._config = {
      show_windows: true,
      show_locks: true,
      ...config,
    };
    // Show loading placeholder until hass arrives
    if (!this._hass) {
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div style="padding: 24px; text-align: center; color: var(--secondary-text-color, #aaa);">
            <ha-icon icon="mdi:car" style="--mdc-icon-size: 32px; opacity: 0.5;"></ha-icon>
            <p style="margin: 8px 0 0; font-size: 13px;">Loading vehicle status…</p>
          </div>
        </ha-card>`;
      return;
    }
    try {
      this._render();
    } catch (err) {
      this._renderError("setConfig", err);
    }
  }

  /**
   * Build a map of translation_key → entity_id for all entities on the same device.
   * Uses hass.entities (the entity registry exposed to the frontend).
   * Handles both full key names and compressed keys (di/pl/tk).
   */
  _buildDeviceEntityMap() {
    if (!this._hass || !this._config.entity) return;

    const entityReg = this._hass.entities;
    if (!entityReg) {
      this._buildDeviceEntityMapFallback();
      return;
    }

    const configEntry = entityReg[this._config.entity];
    if (!configEntry) {
      this._buildDeviceEntityMapFallback();
      return;
    }

    // Support both full and compressed key formats
    const deviceId = configEntry.device_id || configEntry.di;
    if (!deviceId) {
      this._buildDeviceEntityMapFallback();
      return;
    }

    // Only rebuild if device changed
    if (this._deviceId === deviceId && Object.keys(this._keyMap).length > 0) return;

    this._deviceId = deviceId;
    this._keyMap = {};

    for (const [entityId, entry] of Object.entries(entityReg)) {
      const entryDeviceId = entry.device_id || entry.di;
      const entryPlatform = entry.platform || entry.pl;
      const entryTk = entry.translation_key || entry.tk;

      if (entryDeviceId === deviceId && entryPlatform === "hello_smart" && entryTk) {
        this._keyMap[entryTk] = entityId;
      }
    }

    if (Object.keys(this._keyMap).length === 0) {
      this._buildDeviceEntityMapFallback();
    }
  }

  /**
   * Fallback: scan hass.states for entities sharing the same object_id prefix
   * as the configured entity. Maps known suffixes to translation_keys.
   */
  _buildDeviceEntityMapFallback() {
    if (!this._hass || !this._config.entity) return;

    const objectId = this._config.entity.replace(/^[^.]+\./, "");

    // HA-generated entity_id suffix → integration translation_key
    const SUFFIX_TO_TKEY = {
      // Doors (suffix matches translation_key)
      "driver_door": "driver_door",
      "passenger_door": "passenger_door",
      "rear_left_door": "rear_left_door",
      "rear_right_door": "rear_right_door",
      // Trunk/Hood (HA renames from translation_key)
      "boot": "trunk",
      "bonnet": "engine_hood",
      // Windows (suffix matches translation_key)
      "driver_window": "driver_window",
      "passenger_window": "passenger_window",
      "rear_left_window": "rear_left_window",
      "rear_right_window": "rear_right_window",
      "sunroof": "sunroof_open",
      // Locks (HA reorders words in entity_id)
      "driver_door_lock": "door_lock_driver",
      "passenger_door_lock": "door_lock_passenger",
      "rear_left_door_lock": "door_lock_rear_left",
      "rear_right_door_lock": "door_lock_rear_right",
      "boot_lock": "trunk_locked",
      // Image
      "vehicle_image": "vehicle_image_path",
    };

    // Find prefix by matching a known suffix against the configured entity
    let prefix = "";
    for (const suffix of Object.keys(SUFFIX_TO_TKEY)) {
      if (objectId.endsWith(`_${suffix}`)) {
        prefix = objectId.slice(0, -(suffix.length + 1));
        break;
      }
    }

    if (!prefix) {
      const match = objectId.match(/^(.+?)_(?:driver|passenger|rear|trunk|engine|sunroof|door|window|lock|boot|bonnet|vehicle)/);
      if (match) prefix = match[1];
    }
    if (!prefix) return;

    this._keyMap = {};

    for (const entityId of Object.keys(this._hass.states)) {
      const oid = entityId.replace(/^[^.]+\./, "");
      if (!oid.startsWith(prefix + "_")) continue;
      const suffix = oid.slice(prefix.length + 1);

      if (SUFFIX_TO_TKEY[suffix]) {
        this._keyMap[SUFFIX_TO_TKEY[suffix]] = entityId;
      }
    }
  }

  /**
   * Get entity state by translation_key (the integration's sensor description key).
   */
  _getStateByKey(translationKey) {
    const entityId = this._keyMap[translationKey];
    if (!entityId || !this._hass) return null;
    return this._hass.states[entityId] || null;
  }

  _isOnByKey(translationKey) {
    const stateObj = this._getStateByKey(translationKey);
    if (!stateObj) return null;
    return stateObj.state === "on";
  }

  /**
   * Find the lock entity for this device (translation_key: smart_door_lock).
   */
  _getLockEntityId() {
    return this._keyMap["smart_door_lock"] || null;
  }

  /**
   * Toggle the vehicle lock via the lock.lock / lock.unlock service.
   */
  _toggleLock() {
    const lockEntityId = this._getLockEntityId();
    if (!lockEntityId || !this._hass) return;

    const stateObj = this._hass.states[lockEntityId];
    if (!stateObj) return;

    const isLocked = stateObj.state === "locked";
    const service = isLocked ? "unlock" : "lock";

    this._hass.callService("lock", service, { entity_id: lockEntityId });
  }

  /**
   * Check if all door locks are locked (binary sensor "on" = unlocked).
   */
  _checkAllLocked() {
    for (const key of LOCK_KEYS) {
      const isUnlocked = this._isOnByKey(key);
      if (isUnlocked === true) return false;
    }
    return true;
  }

  /**
   * Auto-detect the top-down image URL from the vehicle_image_path sensor.
   */
  _detectImageUrl() {
    if (this._config.image) {
      return this._config.image;
    }

    const imageEntity = this._getStateByKey("vehicle_image_path");
    if (imageEntity && imageEntity.state && imageEntity.state !== "unknown" && imageEntity.state !== "unavailable") {
      return imageEntity.state.replace(/_side\.png$/, "_top.png");
    }

    return "";
  }

  _renderError(phase, err) {
    console.error(`[hello-smart-vehicle-card] Error in ${phase}:`, err);
    if (this.shadowRoot) {
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div style="padding: 16px; color: var(--error-color, #db4437);">
            <b>Hello Smart Vehicle Card Error</b>
            <p style="font-size: 13px; margin: 8px 0 0;">${phase}: ${String(err.message || err)}</p>
            <p style="font-size: 11px; color: var(--secondary-text-color); margin: 4px 0 0;">v${CARD_VERSION} | entity: ${this._config.entity || 'none'} | keys: ${Object.keys(this._keyMap).length}</p>
          </div>
        </ha-card>`;
    }
  }

  set hass(hass) {
    this._hass = hass;
    // Auto-detect entity if not set
    if (!this._config.entity && hass) {
      const detected = HelloSmartVehicleCard._autoDetectEntity(hass);
      if (detected) this._config.entity = detected;
    }
    try {
      this._buildDeviceEntityMap();
      this._render();
    } catch (err) {
      this._renderError("hass", err);
    }
  }

  _render() {
    if (!this._hass || !this._config.entity) return;

    const imageUrl = this._detectImageUrl();
    const showWindows = this._config.show_windows !== false;
    const showLocks = this._config.show_locks !== false;

    // Build door overlay elements
    let doorOverlays = "";
    for (const [key, pos] of Object.entries(DOOR_POSITIONS)) {
      const isOpen = this._isOnByKey(key);
      if (isOpen === null) continue;

      const color = isOpen ? "#F44336" : "#4CAF50";
      const icon = key === "trunk" ? "mdi:car-back" :
                   key === "engine_hood" ? "mdi:car-lifted-pickup" : "mdi:car-door";
      const title = key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
      const stateText = isOpen ? "Open" : "Closed";

      doorOverlays += `
        <div class="overlay-icon" style="left: ${pos.left}%; top: ${pos.top}%;"
             title="${title}: ${stateText}">
          <ha-icon icon="${icon}" style="color: ${color}; --mdc-icon-size: 24px;"></ha-icon>
        </div>`;
    }

    // Build window overlay elements
    let windowOverlays = "";
    if (showWindows) {
      for (const [key, pos] of Object.entries(WINDOW_POSITIONS)) {
        const isOpen = this._isOnByKey(key);
        if (isOpen === null) continue;

        const color = isOpen ? "#FF9800" : "#4CAF50";
        const title = key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
        const stateText = isOpen ? "Open" : "Closed";

        windowOverlays += `
          <div class="overlay-icon window-icon" style="left: ${pos.left}%; top: ${pos.top}%;"
               title="${title}: ${stateText}">
            <ha-icon icon="mdi:window-closed-variant" style="color: ${color}; --mdc-icon-size: 18px;"></ha-icon>
          </div>`;
      }
    }

    // Build lock status row
    let lockRow = "";
    if (showLocks) {
      let lockItems = "";
      const hasLockEntity = !!this._getLockEntityId();
      for (const key of LOCK_KEYS) {
        const isLocked = this._isOnByKey(key);
        if (isLocked === null) continue;

        // In the integration, lock binary sensors are "on" when UNLOCKED
        const color = isLocked ? "#F44336" : "#4CAF50";
        const icon = isLocked ? "mdi:lock-open" : "mdi:lock";
        const label = LOCK_LABELS[key] || key;

        lockItems += `
          <div class="lock-item${hasLockEntity ? ' lock-interactive' : ''}" data-action="toggle-lock"
               title="${label}: ${isLocked ? 'Unlocked' : 'Locked'}${hasLockEntity ? ' (tap to toggle)' : ''}">
            <ha-icon icon="${icon}" style="color: ${color}; --mdc-icon-size: 20px;"></ha-icon>
            <span class="lock-label">${label}</span>
          </div>`;
      }
      if (lockItems) {
        lockRow = `<div class="lock-row">${lockItems}</div>`;
      }
    }

    // Check overall security status
    let allDoorsClosed = true;
    for (const key of Object.keys(DOOR_POSITIONS)) {
      const isOpen = this._isOnByKey(key);
      if (isOpen === true) allDoorsClosed = false;
    }

    const allLocked = this._checkAllLocked();

    const statusColor = (!allDoorsClosed || !allLocked) ? "#F44336" : "#4CAF50";
    const statusIcon = (!allDoorsClosed || !allLocked) ? "mdi:shield-alert" : "mdi:shield-check";
    const statusText = !allDoorsClosed ? "Door Open" :
                       !allLocked ? "Unlocked" : "Secured";

    // Lock toggle button in header (only if lock entity exists)
    const lockEntityId = this._getLockEntityId();
    let lockButton = "";
    if (lockEntityId) {
      const lockState = this._hass.states[lockEntityId];
      const isLocked = lockState && lockState.state === "locked";
      const btnIcon = isLocked ? "mdi:lock-open-outline" : "mdi:lock-outline";
      const btnLabel = isLocked ? "Unlock" : "Lock";
      lockButton = `
        <button class="lock-toggle-btn" data-action="toggle-lock" title="${btnLabel} all doors">
          <ha-icon icon="${btnIcon}" style="--mdc-icon-size: 16px;"></ha-icon>
          ${btnLabel}
        </button>`;
    }

    const imageContent = imageUrl
      ? `<img src="${imageUrl}" alt="Vehicle" class="vehicle-image" />`
      : `<div class="no-image">
           <ha-icon icon="mdi:car" style="--mdc-icon-size: 80px; color: #666;"></ha-icon>
           <p>No vehicle image available</p>
         </div>`;

    this.shadowRoot.innerHTML = `
      <ha-card>
        <style>
          :host {
            --card-bg: var(--ha-card-background, var(--card-background-color, #1e1e1e));
            --text-primary: var(--primary-text-color, #fff);
            --text-secondary: var(--secondary-text-color, #aaa);
          }
          ha-card {
            overflow: hidden;
          }
          .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px 8px;
          }
          .header-title {
            font-size: 16px;
            font-weight: 500;
            color: var(--text-primary);
          }
          .header-right {
            display: flex;
            align-items: center;
            gap: 8px;
          }
          .header-status {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 13px;
            color: ${statusColor};
          }
          .lock-toggle-btn {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border: 1px solid var(--divider-color, #555);
            border-radius: 16px;
            background: transparent;
            color: var(--text-primary);
            font-size: 12px;
            cursor: pointer;
            transition: background 0.2s;
          }
          .lock-toggle-btn:hover {
            background: rgba(255,255,255,0.1);
          }
          .lock-toggle-btn:active {
            background: rgba(255,255,255,0.2);
          }
          .image-container {
            position: relative;
            width: 100%;
            padding: 0 16px 8px;
            box-sizing: border-box;
          }
          .vehicle-image {
            width: 100%;
            height: auto;
            display: block;
            border-radius: 8px;
          }
          .no-image {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 200px;
            color: var(--text-secondary);
          }
          .no-image p {
            margin: 8px 0 0;
            font-size: 13px;
          }
          .overlay-icon {
            position: absolute;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.6);
            border-radius: 50%;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: default;
            transition: background 0.2s;
          }
          .overlay-icon:hover {
            background: rgba(0, 0, 0, 0.8);
          }
          .overlay-icon.window-icon {
            width: 28px;
            height: 28px;
            background: rgba(0, 0, 0, 0.45);
          }
          .lock-row {
            display: flex;
            justify-content: space-around;
            padding: 8px 16px 12px;
            border-top: 1px solid var(--divider-color, #333);
          }
          .lock-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
            cursor: default;
          }
          .lock-item.lock-interactive {
            cursor: pointer;
            transition: opacity 0.2s;
          }
          .lock-item.lock-interactive:hover {
            opacity: 0.7;
          }
          .lock-item.lock-interactive:active {
            opacity: 0.5;
          }
          .lock-label {
            font-size: 11px;
            color: var(--text-secondary);
          }
          .legend {
            display: flex;
            justify-content: center;
            gap: 16px;
            padding: 0 16px 8px;
            font-size: 11px;
            color: var(--text-secondary);
          }
          .legend-item {
            display: flex;
            align-items: center;
            gap: 4px;
          }
          .legend-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
          }
        </style>

        <div class="header">
          <span class="header-title">Vehicle Security</span>
          <div class="header-right">
            ${lockButton}
            <span class="header-status">
              <ha-icon icon="${statusIcon}" style="--mdc-icon-size: 18px;"></ha-icon>
              ${statusText}
            </span>
          </div>
        </div>

        <div class="image-container">
          ${imageContent}
          ${doorOverlays}
          ${windowOverlays}
        </div>

        <div class="legend">
          <span class="legend-item">
            <span class="legend-dot" style="background: #4CAF50;"></span> Closed/Locked
          </span>
          <span class="legend-item">
            <span class="legend-dot" style="background: #F44336;"></span> Open/Unlocked
          </span>
          ${showWindows ? `<span class="legend-item">
            <span class="legend-dot" style="background: #FF9800;"></span> Window Open
          </span>` : ""}
        </div>

        ${lockRow}
      </ha-card>
    `;

    // Bind lock toggle click handlers
    this.shadowRoot.querySelectorAll('[data-action="toggle-lock"]').forEach((el) => {
      el.addEventListener("click", () => this._toggleLock());
    });
  }

  getCardSize() {
    return 5;
  }

  static getConfigElement() {
    return document.createElement("hello-smart-vehicle-card-editor");
  }
}

/**
 * Simple visual editor for the card configuration.
 */
class HelloSmartVehicleCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
  }

  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _render() {
    if (!this._hass) return;

    const entityReg = this._hass.entities || {};

    // Find one representative entity (driver_door) per Smart vehicle device
    const vehicles = [];
    const seenDevices = new Set();
    for (const [entityId, entry] of Object.entries(entityReg)) {
      const pl = entry.platform || entry.pl;
      const tk = entry.translation_key || entry.tk;
      const di = entry.device_id || entry.di;
      if (pl === "hello_smart" && tk === "driver_door" && di && !seenDevices.has(di)) {
        seenDevices.add(di);
        const name = entry.name || entry.en || entityId;
        vehicles.push({ entityId, name, deviceId: di });
      }
    }

    // Auto-select if only one vehicle and no entity configured yet
    if (!this._config.entity && vehicles.length === 1) {
      this._config.entity = vehicles[0].entityId;
      this._fireConfig(this._config);
    }

    // Build vehicle picker — only shown if multiple vehicles exist
    let vehiclePicker = "";
    if (vehicles.length > 1) {
      const opts = vehicles
        .map(v => `<option value="${v.entityId}" ${v.entityId === this._config.entity ? "selected" : ""}>${v.name}</option>`)
        .join("");
      vehiclePicker = `
        <div class="row">
          <label>Vehicle</label>
          <select id="entity">
            ${opts}
          </select>
        </div>`;
    }

    this.shadowRoot.innerHTML = `
      <style>
        .form { padding: 16px; }
        .row { margin-bottom: 12px; }
        label { display: block; margin-bottom: 4px; font-weight: 500; font-size: 13px; color: var(--primary-text-color); }
        select, input[type="text"] {
          width: 100%; padding: 8px; box-sizing: border-box;
          border: 1px solid var(--divider-color, #ccc); border-radius: 4px;
          background: var(--card-background-color, #fff); color: var(--primary-text-color);
        }
        .checkbox-row { display: flex; align-items: center; gap: 8px; }
        .checkbox-row label { margin: 0; font-weight: normal; }
        .auto-note { font-size: 12px; color: var(--secondary-text-color); margin-bottom: 12px; }
      </style>
      <div class="form">
        ${vehicles.length <= 1 ? '<p class="auto-note">Vehicle auto-detected.</p>' : ''}
        ${vehiclePicker}
        <div class="row">
          <label>Image Override (optional)</label>
          <input type="text" id="image" value="${this._config.image || ""}"
                 placeholder="Auto-detected from integration" />
        </div>
        <div class="row checkbox-row">
          <input type="checkbox" id="show_windows" ${this._config.show_windows !== false ? "checked" : ""} />
          <label for="show_windows">Show window overlays</label>
        </div>
        <div class="row checkbox-row">
          <input type="checkbox" id="show_locks" ${this._config.show_locks !== false ? "checked" : ""} />
          <label for="show_locks">Show lock status row</label>
        </div>
      </div>
    `;

    const entitySelect = this.shadowRoot.getElementById("entity");
    if (entitySelect) {
      entitySelect.addEventListener("change", (e) => {
        this._fireConfig({ ...this._config, entity: e.target.value });
      });
    }
    this.shadowRoot.getElementById("image").addEventListener("change", (e) => {
      const val = e.target.value.trim();
      const newConfig = { ...this._config };
      if (val) newConfig.image = val; else delete newConfig.image;
      this._fireConfig(newConfig);
    });
    this.shadowRoot.getElementById("show_windows").addEventListener("change", (e) => {
      this._fireConfig({ ...this._config, show_windows: e.target.checked });
    });
    this.shadowRoot.getElementById("show_locks").addEventListener("change", (e) => {
      this._fireConfig({ ...this._config, show_locks: e.target.checked });
    });
  }

  _fireConfig(config) {
    this._config = config;
    const event = new CustomEvent("config-changed", {
      detail: { config },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }
}

customElements.define("hello-smart-vehicle-card", HelloSmartVehicleCard);
customElements.define("hello-smart-vehicle-card-editor", HelloSmartVehicleCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "hello-smart-vehicle-card",
  name: "Hello Smart Vehicle HUD",
  description: "Top-down vehicle view with door, window, and lock status overlays.",
  preview: true,
  documentationURL: "https://github.com/",
});
