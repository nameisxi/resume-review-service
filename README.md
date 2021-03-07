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

# Palautus 3: Tämän hetkinen toiminnallisuus
Käyttäjä (henkilö joka hakee apua CV:n arviointiin):
- Käyttäjä voi luoda uuden tilin tai kirjautua olemmassa olevalle tilille
- Käyttäjä voi ladata CV:n palveluun PDF muodossa
- Käyttäjä voi kommunikoida arvostelijan kanssa kommenttien muodossa (jokainen CV on kuitenkin yksityinen)

Arvostelija (henkilö joka arvioi CV:itä):
- Arvostelija voi luoda uuden tilin tai kirjautua olemmassa olevalle tilille
- Arvostelija voi arvioida hänelle osoitettuja CV:itä
- Arvostelija voi kommunikoida käyttäjän kanssa kommenttien muodossa

Sovellusta voi testata täällä: http://resume-review-service.herokuapp.com/

Valmiit testikäyttäjät:
| Sähköposti | Salasana | Käyttäjätyyppi |
| ---------- | ---------| -------------- |
| testuser@email.com | 123 | Käyttäjä |
| testreviewer@email.com | 123 | Arvostelija|

TODO:
- refactoring
- push to heroku
- test heroku
- create new test accounts
- update readme


