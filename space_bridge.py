"""Space Bridge - mini-ETL + visualisering.

Filtrerar “outer”-planeter (avstånd ≥ 1.5 AU), konverterar AU till miljoner km,
kategoriserar inner/outer och visualiserar som stapeldiagram. Byggd för att
öva långform till comprehensions, dict-aggregation och enkel plotting.
"""
# NOTE: C1 pipeline lives in count_planets.py (pipeline_run). This file left as-is from CC1.

# Mini projekt för att brygga över de dagar jag ej förstod vissa koncept samt övning med dagens tema som är matplotlib.
# AU = Astronomical Unit - avståndet mellan jorden till solen = 1 AU

# Importerar för att kunna göra en bild(diagram/piechart/etc)
import matplotlib.pyplot as plt
AU_TO_MKM = 149.6  # Konstant högt upp för att undvika problem
THRESHOLD = 1.5  # Variabel högt upp för att undvika att få konsekvenser med det filter jag skapat under

planeter = ["Mercury", "Venus", "Earth", "Mars",
            "Jupiter", "Saturn", "Uranus", "Neptune"]

distans_au = [0.39, 0.72, 1.00, 1.52, 5.20, 9.58, 19.22, 30.05]

assert len(planeter) == len(distans_au)

ytter_planeter = []

for pl, di in zip(planeter, distans_au):  # För planeter
    if di >= THRESHOLD:
        # yttre_planeter.append(pl) = Yttre_planeter.LÄGG TILL(PL)
        ytter_planeter.append(pl)

# Dag 13. Gjorde om lista från långform till comprehension. Behåller långformen för att kunna blicka tillbaka och jämföra
ytter_planeter2 = [pl for pl, di in zip(
    planeter, distans_au) if di >= THRESHOLD]

assert ytter_planeter2 == ytter_planeter
assert "Mars" in ytter_planeter2 and "Earth" not in ytter_planeter2


# ternär comprehension(etiketter) inner/outer
etiketter = ["outer" if di >= THRESHOLD else "inner" for di in distans_au]
assert etiketter.count("outer") == 5 and etiketter.count("inner") == 3

# Dict comprehension

etikett_map = {pl: ("outer" if di >= THRESHOLD else "inner")
               for pl, di in zip(planeter, distans_au)}
# Ännu en sanity check för att se om allting fungerar som det ska.

assert len(etikett_map) == len(planeter) == 8           # en etikett per planet
assert etikett_map["Earth"] == "inner"                  # 1.00 < 1.5
assert etikett_map["Mars"] == "outer"                   # 1.52 >= 1.5
assert [etikett_map[p]
        for p in planeter] == etiketter  # matchar ternära lista


miljoner_km = []

for distans in distans_au:
    miljoner_km.append(round(distans * (AU_TO_MKM), 1))
print(miljoner_km)
# Dag 13. Gjorde om lista från långform till comprehension. Behhåller långformen för att kunna blicka tillbaka och jämföra.
miljoner_km2 = [round(distans * AU_TO_MKM, 1) for distans in distans_au]

assert miljoner_km2 == miljoner_km
assert miljoner_km2[2] == 149.6 and miljoner_km2[-1] == 4495.5

# En tom dict för att lägga ihop antal per etikett
kategorier = {}
for pl, di in zip(planeter, distans_au):
    nyckel = "inner" if di < THRESHOLD else "outer"
    kategorier[nyckel] = kategorier.get(nyckel, 0) + 1

print(kategorier)
print(sum(kategorier.values()) == len(planeter))
assert kategorier == {'inner': 3, 'outer': 5}


# Funktioner.
def outer_planets(planeter, distans_au, threshold=THRESHOLD):
    """Returnerar namn på planeter med avstånd ≥ threshold (i AU).

    Args:
        planeter: Lista med planetnamn.
        distans_au: Motsvarande avstånd i AU (samma ordning som planeter).
        threshold: Gräns i AU för att klassas som 'outer'.

    Returns:
        Lista med planetnamn som uppfyller villkoret.
    """
    outer_list = []
    for planet, dist in zip(planeter, distans_au):
        if dist >= threshold:
            outer_list.append(planet)
    return outer_list


res = outer_planets(planeter, distans_au, THRESHOLD)
print(res)
assert len(res) == 5
assert "Mars" in res and "Earth" not in res

# Funktion för att avrunda


def au_to_mkm(distans_au, faktor=AU_TO_MKM):
    """Konverterar AU till miljoner km (avrundat till 1 decimal).

    Args:
        distans_au: Avstånd i AU.
        faktor: Omvandlingsfaktor (miljoner km per AU).

    Returns:
        Lista med avstånd i miljoner km.
    """
    resultat = []
    for au in distans_au:
        mkm = round(au * faktor, 1)
        resultat.append(mkm)
    return resultat


mkm = au_to_mkm(distans_au)
print(mkm[2], mkm[-1], len(mkm))  # förväntat: 149.6 4495.5 8
assert mkm[2] == 149.6
assert mkm[-1] == 4495.5
assert len(mkm) == 8


# Funktion för att kategorisera
def categorize(planeter, distans_au, threshold=THRESHOLD):
    """Räknar hur många planeter som är 'inner' respektive 'outer'.

    Args:
        planeter: Lista med planetnamn.
        distans_au: Avstånd i AU (samma ordning).
        threshold: Gräns i AU (inner < threshold, outer ≥ threshold).

    Returns:
        Dict med antal per kategori: {'inner': X, 'outer': Y}.
    """
    d = {}
    for pl, di in zip(planeter, distans_au):
        key = "inner" if di < threshold else "outer"
        d[key] = d.get(key, 0) + 1
    return d


counts_from_map = {
    "inner": list(etikett_map.values()).count("inner"),
    "outer": list(etikett_map.values()).count("outer"),
}
assert counts_from_map == categorize(planeter, distans_au) == {
    "inner": 3, "outer": 5}

cat = categorize(planeter, distans_au)
# assert cat == {"inner": 3, "outer": 5}
# assert sum(cat.values()) == len(planeter)


if __name__ == "__main__":
    labels = planeter  # kategorinamn för X-axeln
    values = au_to_mkm(distans_au)  # värde(höjd på staplarna) Y-axeln
    assert len(labels) == len(values)
    # plott
    positions = range(len(values))
    plt.figure()
    plt.bar(positions, values)
    plt.xticks(positions, labels)
    plt.title("Planeters avstånd från solen (miljoner km)")
    plt.xlabel("Planeter")
    plt.ylabel("Miljoner km")
    plt.tight_layout()
    plt.savefig("space_bridge.png")
    # plt.show()
