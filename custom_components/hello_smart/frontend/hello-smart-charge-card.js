/**
 * Hello Smart Charge Status Card
 *
 * A custom Lovelace card bundled with the Hello Smart integration.
 * Displays battery level with a visual gauge, charging status,
 * charge type, range, and live charging metrics.
 *
 * Uses HA's entity registry (hass.entities) for robust device-based
 * entity discovery — works regardless of device name or entity ID prefix.
 *
 * Usage:
 *   type: custom:hello-smart-charge-card
 *   entity: sensor.<any_hello_smart_entity>   # any entity from the device
 *
 * Optional:
 *   show_schedule: true    # show charging schedule info (default: true)
 *   show_12v: false        # show 12V battery info (default: false)
 */

const CHARGE_CARD_VERSION = "1.0.1";

/* eslint-disable no-console */
console.info(
  `%c HELLO-SMART-CHARGE-CARD %c v${CHARGE_CARD_VERSION} `,
  "color: white; background: #00897B; font-weight: bold; padding: 2px 6px; border-radius: 4px 0 0 4px;",
  "color: #00897B; background: #E8E8E8; font-weight: bold; padding: 2px 6px; border-radius: 0 4px 4px 0;"
);

/**
 * Charging state display configuration.
 * Maps ChargingState enum values to icons, colors, and labels.
 */
const CHARGING_STATES = {
  not_charging:         { icon: "mdi:battery",              color: "#9E9E9E", label: "Not Charging" },
  ac_charging:          { icon: "mdi:ev-plug-type2",        color: "#4CAF50", label: "AC Charging" },
  dc_charging:          { icon: "mdi:ev-plug-ccs2",         color: "#2196F3", label: "DC Fast Charging" },
  super_charging:       { icon: "mdi:lightning-bolt",        color: "#2196F3", label: "Super Charging" },
  plugged_not_charging: { icon: "mdi:ev-plug-type2",        color: "#FF9800", label: "Plugged In" },
  boost_charging:       { icon: "mdi:battery-charging-high", color: "#4CAF50", label: "Boost Charging" },
  wireless_charging:    { icon: "mdi:battery-charging-wireless", color: "#4CAF50", label: "Wireless Charging" },
};


class HelloSmartChargeCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._keyMap = {};
    this._deviceId = null;
  }

  static getStubConfig(hass) {
    const entity = HelloSmartChargeCard._autoDetectEntity(hass);
    return { entity: entity || "", show_schedule: true, show_12v: false };
  }

  static _autoDetectEntity(hass) {
    if (!hass) return "";
    const reg = hass.entities || {};
    for (const [entityId, entry] of Object.entries(reg)) {
      const pl = entry.platform || entry.pl;
      const tk = entry.translation_key || entry.tk;
      if (pl === "hello_smart" && tk === "battery_level") return entityId;
    }
    for (const entityId of Object.keys(hass.states || {})) {
      if (entityId.includes("battery_level") && entityId.startsWith("sensor.")) return entityId;
    }
    return "";
  }

  setConfig(config) {
    this._config = {
      show_schedule: true,
      show_12v: false,
      ...config,
    };
    try {
      this._render();
    } catch (err) {
      this._renderError("setConfig", err);
    }
  }

  /**
   * Build a map of translation_key → entity_id for all entities on the same device.
   */
  _buildDeviceEntityMap() {
    if (!this._hass || !this._config.entity) return;

    const entityReg = this._hass.entities;
    if (!entityReg) return;

    const configEntry = entityReg[this._config.entity];
    if (!configEntry) return;

    const deviceId = configEntry.device_id || configEntry.di;
    if (!deviceId) return;

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

  _getStateByKey(translationKey) {
    const entityId = this._keyMap[translationKey];
    if (!entityId || !this._hass) return null;
    return this._hass.states[entityId] || null;
  }

  _getValueByKey(translationKey) {
    const stateObj = this._getStateByKey(translationKey);
    if (!stateObj || stateObj.state === "unknown" || stateObj.state === "unavailable") return null;
    return stateObj.state;
  }

  _getNumericByKey(translationKey) {
    const val = this._getValueByKey(translationKey);
    if (val === null) return null;
    const num = parseFloat(val);
    return isNaN(num) ? null : num;
  }

  _renderError(phase, err) {
    console.error(`[hello-smart-charge-card] Error in ${phase}:`, err);
    if (this.shadowRoot) {
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div style="padding: 16px; color: var(--error-color, #db4437);">
            <b>Hello Smart Charge Card Error</b>
            <p style="font-size: 13px; margin: 8px 0 0;">${phase}: ${String(err.message || err)}</p>
            <p style="font-size: 11px; color: var(--secondary-text-color); margin: 4px 0 0;">v${CHARGE_CARD_VERSION} | entity: ${this._config.entity || 'none'} | keys: ${Object.keys(this._keyMap).length}</p>
          </div>
        </ha-card>`;
    }
  }

  /**
   * Fallback: scan hass.states for entities sharing the same object_id prefix.
   */
  _buildDeviceEntityMapFallback() {
    if (!this._hass || !this._config.entity) return;

    const objectId = this._config.entity.replace(/^[^.]+\./, "");
    const SUFFIX_TO_TKEY = {
      "battery_level": "battery_level",
      "estimated_range": "range_remaining",
      "charging_status": "charging_status",
      "charging_voltage": "charge_voltage",
      "charging_current": "charge_current",
      "dc_charging_current": "dc_charge_current",
      "charging_power": "charging_power",
      "time_to_full_charge": "time_to_full",
      "range_at_full_charge": "range_at_full_charge",
      "average_consumption": "average_power_consumption",
      "scheduled_charging": "charging_schedule_status",
      "scheduled_charge_start": "charging_schedule_start",
      "scheduled_charge_end": "charging_schedule_end",
      "charge_target": "charging_target_soc",
      "12v_battery_voltage": "battery_12v_voltage",
      "12v_battery_level": "battery_12v_level",
      "charger": "charger_connected",
    };

    let prefix = "";
    for (const suffix of Object.keys(SUFFIX_TO_TKEY)) {
      if (objectId.endsWith(`_${suffix}`) || objectId === suffix) {
        prefix = objectId.endsWith(`_${suffix}`) ? objectId.slice(0, -(suffix.length + 1)) : "";
        break;
      }
    }
    if (!prefix) {
      const match = objectId.match(/^(.+?)_(?:battery|charging|estimated|scheduled|average|dc_|12v_|charge_|time_to)/);
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

  set hass(hass) {
    this._hass = hass;
    if (!this._config.entity && hass) {
      const detected = HelloSmartChargeCard._autoDetectEntity(hass);
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

    // ── Gather data ─────────────────────────────────────────────────
    const batteryLevel = this._getNumericByKey("battery_level");
    const range = this._getNumericByKey("range_remaining");
    const chargingStatus = this._getValueByKey("charging_status");
    const chargerConnected = this._getValueByKey("charger_connected");
    const chargeVoltage = this._getNumericByKey("charge_voltage");
    const chargeCurrent = this._getNumericByKey("charge_current");
    const dcChargeCurrent = this._getNumericByKey("dc_charge_current");
    const chargingPower = this._getNumericByKey("charging_power");
    const timeToFull = this._getNumericByKey("time_to_full");
    const rangeAtFull = this._getNumericByKey("range_at_full_charge");
    const avgConsumption = this._getNumericByKey("average_power_consumption");

    // Schedule
    const scheduleStatus = this._getValueByKey("charging_schedule_status");
    const scheduleStart = this._getValueByKey("charging_schedule_start");
    const scheduleEnd = this._getValueByKey("charging_schedule_end");
    const targetSoc = this._getNumericByKey("charging_target_soc");

    // 12V
    const battery12vVoltage = this._getNumericByKey("battery_12v_voltage");
    const battery12vLevel = this._getNumericByKey("battery_12v_level");

    // ── Derive display values ───────────────────────────────────────
    const isCharging = chargingStatus && chargingStatus !== "not_charging" && chargingStatus !== "plugged_not_charging";
    const isPluggedIn = chargerConnected === "on";
    const stateInfo = CHARGING_STATES[chargingStatus] || CHARGING_STATES.not_charging;

    const pct = batteryLevel !== null ? Math.max(0, Math.min(100, batteryLevel)) : 0;
    const batteryColor = pct > 60 ? "#4CAF50" : pct > 20 ? "#FF9800" : "#F44336";

    // Time to full display
    let timeToFullDisplay = "";
    if (timeToFull !== null && isCharging) {
      const hrs = Math.floor(timeToFull / 60);
      const mins = Math.round(timeToFull % 60);
      timeToFullDisplay = hrs > 0 ? `${hrs}h ${mins}m` : `${mins}m`;
    }

    // Active current (prefer DC if DC charging)
    const activeCurrent = chargingStatus === "dc_charging" && dcChargeCurrent !== null
      ? dcChargeCurrent : chargeCurrent;

    // ── Build charging metrics (only when charging) ─────────────────
    let chargingMetrics = "";
    if (isCharging) {
      let rows = "";
      if (chargingPower !== null) {
        rows += this._metricRow("mdi:flash", "Power", `${chargingPower.toFixed(1)} kW`);
      }
      if (chargeVoltage !== null) {
        rows += this._metricRow("mdi:sine-wave", "Voltage", `${chargeVoltage.toFixed(0)} V`);
      }
      if (activeCurrent !== null) {
        rows += this._metricRow("mdi:current-ac", "Current", `${activeCurrent.toFixed(1)} A`);
      }
      if (timeToFullDisplay) {
        rows += this._metricRow("mdi:timer-sand", "Time to Full", timeToFullDisplay);
      }
      if (rangeAtFull !== null) {
        rows += this._metricRow("mdi:map-marker-distance", "Range at Full", `${Math.round(rangeAtFull)} km`);
      }
      if (rows) {
        chargingMetrics = `
          <div class="section">
            <div class="section-title">Charging Details</div>
            <div class="metrics-grid">${rows}</div>
          </div>`;
      }
    }

    // ── Build info strip (always visible) ───────────────────────────
    let infoItems = "";
    if (range !== null) {
      infoItems += `
        <div class="info-item">
          <ha-icon icon="mdi:road-variant" style="--mdc-icon-size: 18px;"></ha-icon>
          <span class="info-value">${Math.round(range)} km</span>
          <span class="info-label">Range</span>
        </div>`;
    }
    if (avgConsumption !== null) {
      infoItems += `
        <div class="info-item">
          <ha-icon icon="mdi:leaf" style="--mdc-icon-size: 18px;"></ha-icon>
          <span class="info-value">${avgConsumption.toFixed(1)}</span>
          <span class="info-label">Wh/km</span>
        </div>`;
    }
    infoItems += `
      <div class="info-item">
        <ha-icon icon="${isPluggedIn ? 'mdi:power-plug' : 'mdi:power-plug-off'}"
                 style="--mdc-icon-size: 18px; color: ${isPluggedIn ? '#4CAF50' : 'var(--text-secondary)'};"></ha-icon>
        <span class="info-value">${isPluggedIn ? "Connected" : "Unplugged"}</span>
        <span class="info-label">Charger</span>
      </div>`;

    // ── Schedule section ────────────────────────────────────────────
    let scheduleSection = "";
    if (this._config.show_schedule && scheduleStatus) {
      const isActive = scheduleStatus === "active";
      let scheduleInfo = "";
      if (isActive && scheduleStart) {
        scheduleInfo += this._metricRow("mdi:clock-start", "Start", scheduleStart);
      }
      if (isActive && scheduleEnd) {
        scheduleInfo += this._metricRow("mdi:clock-end", "End", scheduleEnd);
      }
      if (isActive && targetSoc !== null) {
        scheduleInfo += this._metricRow("mdi:battery-arrow-up", "Target", `${targetSoc}%`);
      }
      scheduleSection = `
        <div class="section">
          <div class="section-title">
            <ha-icon icon="${isActive ? 'mdi:calendar-clock' : 'mdi:calendar-remove'}" style="--mdc-icon-size: 16px;"></ha-icon>
            Scheduled Charging: ${isActive ? "Active" : "Inactive"}
          </div>
          ${scheduleInfo ? `<div class="metrics-grid">${scheduleInfo}</div>` : ""}
        </div>`;
    }

    // ── 12V section ─────────────────────────────────────────────────
    let section12v = "";
    if (this._config.show_12v && (battery12vVoltage !== null || battery12vLevel !== null)) {
      let rows12v = "";
      if (battery12vVoltage !== null) {
        rows12v += this._metricRow("mdi:car-battery", "Voltage", `${battery12vVoltage.toFixed(1)} V`);
      }
      if (battery12vLevel !== null) {
        rows12v += this._metricRow("mdi:battery-medium", "Level", `${battery12vLevel}%`);
      }
      section12v = `
        <div class="section">
          <div class="section-title">12V Battery</div>
          <div class="metrics-grid">${rows12v}</div>
        </div>`;
    }

    // ── Render ───────────────────────────────────────────────────────
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
          .header-status {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: ${stateInfo.color};
          }

          /* ── Battery gauge ── */
          .gauge-container {
            padding: 8px 16px 4px;
          }
          .gauge-bar-bg {
            width: 100%;
            height: 28px;
            background: rgba(255,255,255,0.08);
            border-radius: 14px;
            overflow: hidden;
            position: relative;
          }
          .gauge-bar-fill {
            height: 100%;
            border-radius: 14px;
            background: ${batteryColor};
            width: ${pct}%;
            transition: width 0.6s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            box-sizing: border-box;
            min-width: 40px;
          }
          .gauge-pct {
            font-size: 14px;
            font-weight: 700;
            color: #fff;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
          }
          .gauge-label {
            display: flex;
            justify-content: space-between;
            padding: 4px 4px 0;
            font-size: 11px;
            color: var(--text-secondary);
          }

          /* ── Info strip ── */
          .info-strip {
            display: flex;
            justify-content: space-around;
            padding: 12px 16px;
          }
          .info-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
            color: var(--text-primary);
          }
          .info-value {
            font-size: 14px;
            font-weight: 600;
          }
          .info-label {
            font-size: 11px;
            color: var(--text-secondary);
          }

          /* ── Sections ── */
          .section {
            border-top: 1px solid var(--divider-color, #333);
            padding: 10px 16px;
          }
          .section-title {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-primary);
            margin-bottom: 8px;
          }
          .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px 16px;
          }
          .metric-row {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
          }
          .metric-label {
            color: var(--text-secondary);
          }
          .metric-value {
            color: var(--text-primary);
            font-weight: 500;
            margin-left: auto;
          }

          /* ── Charging animation ── */
          ${isCharging ? `
          @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.3); }
            50% { box-shadow: 0 0 12px 4px rgba(76, 175, 80, 0.15); }
          }
          .gauge-bar-bg {
            animation: pulse-glow 2s ease-in-out infinite;
          }
          ` : ""}
        </style>

        <div class="header">
          <span class="header-title">Charge Status</span>
          <span class="header-status">
            <ha-icon icon="${stateInfo.icon}" style="--mdc-icon-size: 18px;"></ha-icon>
            ${stateInfo.label}
          </span>
        </div>

        <div class="gauge-container">
          <div class="gauge-bar-bg">
            <div class="gauge-bar-fill">
              <span class="gauge-pct">${batteryLevel !== null ? `${Math.round(batteryLevel)}%` : "—"}</span>
            </div>
          </div>
          <div class="gauge-label">
            <span>0%</span>
            <span>100%</span>
          </div>
        </div>

        <div class="info-strip">
          ${infoItems}
        </div>

        ${chargingMetrics}
        ${scheduleSection}
        ${section12v}
      </ha-card>
    `;
  }

  _metricRow(icon, label, value) {
    return `
      <div class="metric-row">
        <ha-icon icon="${icon}" style="--mdc-icon-size: 16px; color: var(--text-secondary);"></ha-icon>
        <span class="metric-label">${label}</span>
        <span class="metric-value">${value}</span>
      </div>`;
  }

  getCardSize() {
    return 4;
  }

  static getConfigElement() {
    return document.createElement("hello-smart-charge-card-editor");
  }
}

/**
 * Visual editor for the charge card configuration.
 */
class HelloSmartChargeCardEditor extends HTMLElement {
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

    // Find one representative entity (battery_level) per Smart vehicle device
    const vehicles = [];
    const seenDevices = new Set();
    for (const [entityId, entry] of Object.entries(entityReg)) {
      const pl = entry.platform || entry.pl;
      const tk = entry.translation_key || entry.tk;
      const di = entry.device_id || entry.di;
      if (pl === "hello_smart" && tk === "battery_level" && di && !seenDevices.has(di)) {
        seenDevices.add(di);
        const name = entry.name || entry.en || entityId;
        vehicles.push({ entityId, name, deviceId: di });
      }
    }

    if (!this._config.entity && vehicles.length === 1) {
      this._config.entity = vehicles[0].entityId;
      this._fireConfig(this._config);
    }

    let vehiclePicker = "";
    if (vehicles.length > 1) {
      const opts = vehicles
        .map(v => `<option value="${v.entityId}" ${v.entityId === this._config.entity ? "selected" : ""}>${v.name}</option>`)
        .join("");
      vehiclePicker = `
        <div class="row">
          <label>Vehicle</label>
          <select id="entity">${opts}</select>
        </div>`;
    }

    this.shadowRoot.innerHTML = `
      <style>
        .form { padding: 16px; }
        .row { margin-bottom: 12px; }
        label { display: block; margin-bottom: 4px; font-weight: 500; font-size: 13px; color: var(--primary-text-color); }
        select {
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
        <div class="row checkbox-row">
          <input type="checkbox" id="show_schedule" ${this._config.show_schedule !== false ? "checked" : ""} />
          <label for="show_schedule">Show charging schedule</label>
        </div>
        <div class="row checkbox-row">
          <input type="checkbox" id="show_12v" ${this._config.show_12v === true ? "checked" : ""} />
          <label for="show_12v">Show 12V battery</label>
        </div>
      </div>
    `;

    const entitySelect = this.shadowRoot.getElementById("entity");
    if (entitySelect) {
      entitySelect.addEventListener("change", (e) => {
        this._fireConfig({ ...this._config, entity: e.target.value });
      });
    }
    this.shadowRoot.getElementById("show_schedule").addEventListener("change", (e) => {
      this._fireConfig({ ...this._config, show_schedule: e.target.checked });
    });
    this.shadowRoot.getElementById("show_12v").addEventListener("change", (e) => {
      this._fireConfig({ ...this._config, show_12v: e.target.checked });
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

customElements.define("hello-smart-charge-card", HelloSmartChargeCard);
customElements.define("hello-smart-charge-card-editor", HelloSmartChargeCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "hello-smart-charge-card",
  name: "Hello Smart Charge Status",
  description: "Battery level, charging status, type, range, and live charging metrics.",
  preview: true,
  documentationURL: "https://github.com/",
});
