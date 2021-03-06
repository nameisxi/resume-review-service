# Resume review

## HUOM 1: Heroku käyttää ephemeral filysystemiä, joka restarttaa jokaisen päivityksen/buildin yhteydessä, joten osa CV:istä saattaa palauttaa 404 Not Found errorin.
## Huom 2: upotettu PDF viewer ei välttämättä toimi Safarilla kaikilla CV:illä.

Resume review palvelussa voi antaa ja saada arvosteluja CV:istä. Palvelu toimii siten, että käyttäjä lataa sivulle CV:nsä, jonka jälkeen palvelu osoittaa CV:n jollekkin arvostelijoista. Seuraavaksi arvostelija antaa palautetta CV:stä ja saa arvosteltavaksi seuraavan CV:n jonossa. Arvostelija voi edelleen jatkaa kommunikointia käyttäjän kanssa. CV:t ja keskustelut (kommentit) pysyvät käyttäjän ja arvostelijan välisinä, eivätkä muut käyttäjät näe niitä.

Tässä Resume review palvelun keskeisimmät ominaisuudet:

Käyttäjä (henkilö joka hakee apua CV:n arviointiin):
- Käyttäjä voi luoda uuden tilin tai kirjautua olemmassa olevalle tilille
- Käyttäjä voi ladata CV:n palveluun PDF muodossa
- Käyttäjä voi kommunikoida arvostelijan kanssa kommenttien muodossa (jokainen CV on kuitenkin yksityinen)
- Käyttäjä voi antaa tyytyväisyysarvion CV neuvoista.

Arvostelija (henkilö joka arvioi CV:itä):
- Arvostelija voi luoda uuden tilin tai kirjautua olemmassa olevalle tilille
- Arvostelija voi arvioida hänelle osoitettuja CV:itä
- Arvostelija voi kommunikoida käyttäjän kanssa kommenttien muodossa

# Lopullinen palautus: Tämän hetkinen toiminnallisuus
Käyttäjä (henkilö joka hakee apua CV:n arviointiin):
- Käyttäjä voi luoda uuden tilin tai kirjautua olemmassa olevalle tilille
- Käyttäjä voi ladata CV:n palveluun PDF muodossa
- Käyttäjä voi kommunikoida arvostelijan kanssa kommenttien muodossa (jokainen CV on kuitenkin yksityinen)
- Käyttäjä voi arvostella saamaansa palautetta asteikolla 1-5
- Käyttäjä voi poistaa yksittäisiä CV:itä
- Käyttäjä voi vaihtaa salasanan
- Käyttäjä voi poistaa tilinsä (soft delete)
- Käyttäjä saa tiedon, jos jonkin hänen CV:nsä arvioijista poistaa tilinsä käytöstä (tulevaisuudessa käyttäjä voi vielä pyytää uuden arvioijan saamista, mikäli hänen tapauksensa on vielä kesken, tai hän tarvitsee muuten apua)  

Arvostelija (henkilö joka arvioi CV:itä):
- Arvostelija voi luoda uuden tilin tai kirjautua olemmassa olevalle tilille
- Arvostelija voi arvioida (eli kommentoida) hänelle osoitettuja CV:itä
- Arvostelija voi kommunikoida käyttäjän kanssa kommenttien muodossa
- Arvostelija voi vaihtaa salasanan
- Arvostelija voi passivoida tilinsä (disable account - tähän on monta syytä, kuten referenssien säilyttäminen, jottei käyttäjä menetä CV:tä tai hänen saamaansa feedbackkia, kuin myös työmäärän allokointi arvostelijoiden keskuudessa. Mikäli lisäkysymyksiä herää, vastaan mielelläni)

Sovellusta voi testata täällä: http://resume-review-service.herokuapp.com/

Valmiit testikäyttäjät:
| Sähköposti | Salasana | Käyttäjätyyppi |
| ---------- | ---------| -------------- |
| user@email.com | 12345678 | Käyttäjä |
| reviewer@admin.fi | 12345678 | Arvostelija|



