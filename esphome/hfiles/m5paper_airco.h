#pragma once
// Helpers voor het M5Paper paneel — implementatie van het "M5Paper E-ink Design
// System" (zwart/wit, 960x540, hand-gepositioneerd in px). Meegecompileerd via de
// ESPHome `includes:` directive (zelfde unit als text_utils.h).
//
// Tokens: zwart 0x000000 / wit 0xFFFFFF / lichtgrijs 0xC0C0C0 (alleen grote vlakken).
// Strokes: 2px (dun, onderstreping) · 3px (normaal, randen/lijnen) · 4px (nadruk).
// Hoeken: recht (radius 0). Roboto-tekst + Material Design Icons.

static const int SCREEN_W = 960;
static const int SCREEN_H = 540;

// Dikke horizontale/verticale lijn via filled_rectangle (e-ink wil >=2px structuur).
void eink_hline(esphome::display::Display *it, int x, int y, int w, int t) {
  it->filled_rectangle(x, y, w, t);
}
void eink_vline(esphome::display::Display *it, int x, int y, int h, int t) {
  it->filled_rectangle(x, y, t, h);
}

// Dikke outline-rechthoek: t geneste 1px-rechthoeken (rectangle() is maar 1px).
void eink_rect(esphome::display::Display *it, int x, int y, int w, int h, int t) {
  for (int i = 0; i < t; i++) {
    it->rectangle(x + i, y + i, w - 2 * i, h - 2 * i);
  }
}

// Numerieke waarde met komma-decimaal (NL) + suffix. Zwart of wit.
void eink_val(esphome::display::Display *it, int x, int y, esphome::font::Font *f,
              TextAlign a, float v, int dec, const char *suffix) {
  char num[24], out[40];
  snprintf(num, sizeof(num), "%.*f", dec, v);
  for (char *p = num; *p; ++p)
    if (*p == '.') *p = ',';
  snprintf(out, sizeof(out), "%s%s", num, suffix);
  it->print(x, y, f, a, out);
}
void eink_val_w(esphome::display::Display *it, int x, int y, esphome::font::Font *f,
                TextAlign a, float v, int dec, const char *suffix) {
  // LET OP: deze driver mapt color.raw_32 & 0x0F -> Color(0,0,0) rendert WIT,
  // Color(255,255,255) rendert ZWART. Inverse (witte) inhoud = Color(0,0,0).
  esphome::Color white(0, 0, 0);
  char num[24], out[40];
  snprintf(num, sizeof(num), "%.*f", dec, v);
  for (char *p = num; *p; ++p)
    if (*p == '.') *p = ',';
  snprintf(out, sizeof(out), "%s%s", num, suffix);
  it->print(x, y, f, white, a, out);
}

// HVAC-mode knop (126x92): icoon boven, label onder.
// actief => zwart gevuld vlak + witte inhoud · default => 3px outline + zwart.
void eink_mode_btn(esphome::display::Display *it, int x, int y, int w, int h,
                   esphome::font::Font *icon_f, const char *icon,
                   esphome::font::Font *label_f, const char *label, bool active) {
  // Color(0,0,0) rendert WIT op deze driver (raw_32 & 0x0F; 0xF=zwart).
  esphome::Color white(0, 0, 0);
  if (active) {
    it->filled_rectangle(x, y, w, h);
    it->print(x + 45, y + 14, icon_f, white, icon);
    it->print(x + w / 2, y + 56, label_f, white, TextAlign::TOP_CENTER, label);
  } else {
    eink_rect(it, x, y, w, h, 3);
    it->print(x + 45, y + 14, icon_f, icon);
    it->print(x + w / 2, y + 56, label_f, TextAlign::TOP_CENTER, label);
  }
}

// Tekst-only keuzeknop (bv. swing-standen): label horizontaal+verticaal gecentreerd.
// actief => zwart gevuld vlak + witte tekst · default => 3px outline + zwart.
void eink_text_btn(esphome::display::Display *it, int x, int y, int w, int h,
                   esphome::font::Font *label_f, const char *label, bool active) {
  esphome::Color white(0, 0, 0);  // = WIT op deze driver
  if (active) {
    it->filled_rectangle(x, y, w, h);
    it->print(x + w / 2, y + h / 2, label_f, white, TextAlign::CENTER, label);
  } else {
    eink_rect(it, x, y, w, h, 3);
    it->print(x + w / 2, y + h / 2, label_f, TextAlign::CENTER, label);
  }
}

// ----- Airco swing/fan: HA-modestring <-> index, en korte ventilator-labels -----
// swing_modes: "Up/Down Auto","Highest","Middle","Normal","Lowest","3D Auto"
static const char *SWING_MODES[6] = {"Up/Down Auto", "Highest", "Middle",
                                     "Normal", "Lowest", "3D Auto"};
// fan_modes: "auto","1 Lowest","2 Low","3 High","4 Highest"
static const char *FAN_MODES[5] = {"auto", "1 Lowest", "2 Low", "3 High",
                                   "4 Highest"};

int swing_index(const std::string &s) {
  for (int i = 0; i < 6; i++)
    if (s == SWING_MODES[i]) return i;
  return -1;
}
int fan_index(const std::string &s) {
  for (int i = 0; i < 5; i++)
    if (s == FAN_MODES[i]) return i;
  return -1;
}
// Kort label tussen de ventilator-stepperknoppen.
const char *fan_short(int idx) {
  static const char *labels[5] = {"Auto", "1", "2", "3", "4"};
  if (idx < 0 || idx > 4) return "--";
  return labels[idx];
}

// ----- Nederlandse datum-labels voor het hoofdscherm -----
// ESPTime: day_of_week 1=zondag..7=zaterdag · month 1..12
const char *nl_weekday(int dow) {
  static const char *d[8] = {"", "zondag", "maandag", "dinsdag", "woensdag",
                             "donderdag", "vrijdag", "zaterdag"};
  if (dow < 1 || dow > 7) return "";
  return d[dow];
}
const char *nl_month(int m) {
  static const char *mo[13] = {"", "januari", "februari", "maart", "april",
                               "mei", "juni", "juli", "augustus", "september",
                               "oktober", "november", "december"};
  if (m < 1 || m > 12) return "";
  return mo[m];
}

// Bron-icoon per kalender-code (gelijk aan de HA-entiteit-iconen, in ic28).
const char *cal_glyph(char c) {
  switch (c) {
    case 'g': return "\U000F0827";  // home-heart        (Gezin)
    case 'b': return "\U000F0643";  // face-man          (Bram)
    case 'm': return "\U000F1077";  // face-woman        (Maninne)
    case 'j': return "\U000F0644";  // face-man-profile  (Jozua)
    case 'a': return "\U000F15CE";  // face-woman-shimmer (Anne-Lize)
    case 'w': return "\U000F010B";  // car               (BMW)
    default:  return "";
  }
}

// Eén geparseerde agenda-regel. tm = "HH:MM" of "HH:MM-HH:MM" (start[-eind]),
// leeg = hele-dag. code = bronkalender-letter.
struct AgendaItem {
  bool valid;
  char code;
  std::string tm;
  std::string title;
};

// Parse "CODE|tijd|titel" (nieuw) of "tijd|titel" (oud) — tolerant zodat firmware en
// HA-template-deploy even uit de pas mogen lopen. Lege string -> valid=false.
AgendaItem agenda_parse(const std::string &s) {
  AgendaItem a{false, ' ', std::string(""), std::string("")};
  if (s.empty()) return a;
  a.valid = true;
  size_t b1 = s.find('|');
  std::string f1 = (b1 == std::string::npos) ? s : s.substr(0, b1);
  std::string rest = (b1 == std::string::npos) ? std::string("") : s.substr(b1 + 1);
  if (f1.size() == 1 && (f1[0] == 'g' || f1[0] == 'b' || f1[0] == 'm' ||
                         f1[0] == 'j' || f1[0] == 'a' || f1[0] == 'w')) {
    a.code = f1[0];
    size_t b2 = rest.find('|');
    a.tm = (b2 == std::string::npos) ? std::string("") : rest.substr(0, b2);
    a.title = (b2 == std::string::npos) ? rest : rest.substr(b2 + 1);
  } else {
    a.tm = f1;
    a.title = rest;
  }
  return a;
}

// Startminuten sinds middernacht uit tm ("HH:MM..."); hele-dag/onbekend -> 0
// (sorteert als "vroegst", dus boven de nu-lijn).
int agenda_start_min(const AgendaItem &a) {
  if (a.tm.size() < 5 || a.tm[2] != ':') return 0;
  int hh = (a.tm[0] - '0') * 10 + (a.tm[1] - '0');
  int mm = (a.tm[3] - '0') * 10 + (a.tm[4] - '0');
  if (hh < 0 || hh > 23 || mm < 0 || mm > 59) return 0;
  return hh * 60 + mm;
}

// Teken één agenda-regel: tijd(range) @340 · bron-icoon @500 · titel @540.
void eink_agenda_draw(esphome::display::Display *it, const AgendaItem &a, int y,
                      esphome::font::Font *time_f, esphome::font::Font *title_f,
                      esphome::font::Font *badge_f, esphome::font::Font *icon_f) {
  if (!a.valid) return;
  if (a.tm.empty()) {
    eink_rect(it, 340, y - 4, 112, 40, 2);
    it->print(396, y + 16, badge_f, TextAlign::CENTER, "Hele dag");
  } else {
    it->print(340, y, time_f, a.tm.c_str());
  }
  const char *g = cal_glyph(a.code);
  if (g[0] != '\0') it->print(500, y, icon_f, g);
  it->print(540, y, title_f, a.title.c_str());
}
