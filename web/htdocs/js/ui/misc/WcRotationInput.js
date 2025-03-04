/**
 * https://dev.to/ndesmic/how-to-make-a-rotational-knob-input-with-web-components-43e3
 */
class WcRotationInput extends HTMLElement {
    #center = {};
    #currentValue = 0;

    #position = 0;
    #startPosition = 0;
    
    static #triggerType = ["manipulate", "settled"];
    static observedAttributes = ["displayvalue", "trigger"];
    
    #trigger = "manipulate";
    #displayValue = false;
    
    constructor() {
        super();
        this.bind(this);
    }

    #fireEvent(element, eventName, data, bubbles = true, cancelable = true) {
        const event = document.createEvent("HTMLEvents");
        event.initEvent(eventName, bubbles, cancelable);
        if (data) {
            event.data = data;
        }
        return element.dispatchEvent(event);
    }
    
    #validateEnum(val, choices){
        if(choices.includes(val)){
            return val;
        }
        throw new Error(`invalid type, only ${choices.join(",")} allowed.`);
    }
    
    bind(element) {
        this.render = this.render.bind(element);
        this.cacheDom = this.cacheDom.bind(element);
        this.attachEvents = this.attachEvents.bind(element);
        this.onPointerDown = this.onPointerDown.bind(element);
        this.onPointerMove = this.onPointerMove.bind(element);
        this.onPointerUp = this.onPointerUp.bind(element);
    }

    render() {
        this.shadow = this.attachShadow({ mode: "open" });

        this.shadow.innerHTML = `
            <style>
                :host {
                    display: inline-flex;
                    flex-flow: row nowrap;
                    gap: 0.5rem;
                    align-items: center;
                    width: 8rem;
                    height: 2rem;
                    --half-stroke: calc(var(--stroke-width, 1px) / 2);
                }
                svg {
                    width: auto;
                    height: 100%;
                }
                circle {
                    r : calc(50% - var(--half-stroke));
                    cx : 50%;
                    cy : 50%;
                    fill: var(--fill-color, #fff);
                    /*stroke-width: var(--stoke-width, 1px);*/
                    /*stroke: var(--stroke-color, #000);*/
                }
                #pointer {
                    stroke-width: var(--stoke-width, 1px);
                    stroke: var(--stroke-color, #000);
                    transform-origin: center center;
                }
                #value {
                    user-select: none;
                }
            </style>
            <svg viewBox="0 0 16 16">
                <circle />
                <line x1="50%" y1="50%" x2="100%" y2="50%" id="pointer"/>
            </svg>
            <div id="value"></div>
        `;
    }

    connectedCallback() {
        this.render();
        this.cacheDom();
        this.attachEvents();
    }
    
    cacheDom() {
        this.dom = {
            input: this.querySelector("input"),
            pointer: this.shadow.querySelector("#pointer"),
            value: this.shadow.querySelector("#value"),
            svg: this.shadow.querySelector("svg")
        };
    }

    attachEvents() {
        this.dom.svg.addEventListener("pointerdown", this.onPointerDown);
    }

    onPointerDown(e) {
        this.#center = {
            x: e.pageX,
            y: e.pageY
        }
        
        this.#startPosition = this.#position;
        
        // const rect = this.dom.svg.getBoundingClientRect();
        // this.#center = { x: rect.x + (rect.width / 2), y: rect.y + (rect.height / 2) };
        document.addEventListener("pointermove", this.onPointerMove);
        document.addEventListener("pointerup", this.onPointerUp);
    }

    onPointerMove(e) {
        const offset = e.pageX - this.#center.x;
        this.#position = Math.round(this.#startPosition + offset);

        this.dom.pointer.style = `transform: rotateZ(${this.#position}deg)`;

        if (this.#displayValue) {
            this.dom.value.textContent = this.#position;
        }

        if(this.#trigger === "manipulate"){
            this.dom.input.value = this.#position;
            this.#fireEvent(this.dom.input, "input");
            this.#fireEvent(this.dom.input, "change");
        } else {
            this.#currentValue = this.#position;
        }
    }

    onPointerUp() {
        document.removeEventListener("pointermove", this.onPointerMove);
        document.removeEventListener("pointerup", this.onPointerUp);
        if(this.#trigger === "settled"){
            this.dom.input.value = this.#currentValue;
            this.#fireEvent(this.dom.input, "input");
            this.#fireEvent(this.dom.input, "change");
        }
    }

    attributeChangedCallback(name, oldValue, newValue) {
        this[name] = newValue;
    }

    set trigger(val) {
        this.#trigger = this.#validateEnum(val, WcRotationInput.#triggerType);
    }

    set displayvalue(val) {
        this.#displayValue = !!val;
    }
}

customElements.define("wc-rotation-input", WcRotationInput);