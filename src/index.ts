import { css, PropertyValues } from 'lit';
import { html, LitElement } from 'lit-element/lit-element.js';
import { customElement, property, query } from 'lit/decorators.js';

@customElement("kicker-player-profile")
export class ProfileElement extends LitElement {
  static override readonly styles = css`div {
    font-size: small; 
  }
  * {
    margin: 4px;
  }
  :host {
    display: block;
    width: max-content;
  }`;

  @query("form")
  protected _form!: HTMLFormElement; 

  @property()
  public mode: "create" | "update" | "view" = "create";

  @property()
  public name = ""

  @property()
  public location: "Berlin" | "Munich" | "Würzburg" = "Berlin";

  submit(event: Event) {
    event.preventDefault();
    if (!event.target) {
      return;
    }
    if (this.mode === "view") {
      this.mode = "update";
      return;
    }
    const data = new FormData(event.target as HTMLFormElement);
    this.name = (data.get("name") ?? this.name ?? "") as any;
    this.location = (data.get("location") ?? "Berlin") as any;
    fetch("/profiles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({name: this.name, location: this.location})
    }).then(() => {
      this.mode = "view";
    });
  }

  delete(event: Event) {
    event.preventDefault();
    const data = new FormData(this._form);
    this.name = (data.get("name") ?? this.name ?? "") as any;
    fetch(`/profiles/${this.name}`, {
      method: "DELETE"
    }).then(() => {
      this.mode = "create";
      this.name = "";
      this.location = "Berlin";
    });
  }

  override update(changedProperties: PropertyValues) {
    if (changedProperties.has("name") && this.name && this.mode !== "create") {
      fetch(`/profiles/${this.name}`)
      .then(response => response.json())
      .then(response => {
        this.name = response.name;
        this.location = response.location;
      });
    }
    super.update(changedProperties);
  }

  override render() {
    switch (this.mode) {
      case "create":
      case "update":
      case "view":
        return html`
          <div>${this.mode === "create" ? "Spieler anlegen" : this.mode === "update" ? "Spieler aktualisieren" : "Spielerinformationen"}</div>
          <form @submit=${this.submit}>
            <input type="text" placeholder="Spielername eingeben" name="name" .value="${this.name}" ?disabled=${this.mode === "update" || this.mode === "view"}/>
            <select name="location" .value="${this.location}" ?disabled=${this.mode === "view"}>
              <option value="Berlin">Berlin</option>
              <option value="Munich">München</option>
              <option value="Würzburg">Würzburg</option>
            </select>
            <input type="submit" value="${this.mode.match(/^(create|update)$/) ? (this.mode == "create" ? "Erstellen" : "Aktualisieren") : "Bearbeiten"}">
            ${this.mode === "update" ? html`<button @click="${this.delete}">Löschen</button>` : html``}
          </form>
        `;
      default:
        return html``;
    }
  }
}

@customElement("kicker-team")
export class TournamentElement extends LitElement {

}

@customElement("app-main")
export class AppMainElement extends LitElement {
  static override readonly styles = css`kicker-player-profile { border: 1px solid; }`;

  override render() {
    return html`
      <kicker-player-profile mode="create"></kicker-player-profile>
      <kicker-player-profile mode="update"></kicker-player-profile>
      <kicker-player-profile mode="view" name="otto"></kicker-player-profile>
    `;
  }
}