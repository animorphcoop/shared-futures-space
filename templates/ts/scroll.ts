import {expose} from "@/templates/ts/utils.ts";

expose({ stopBodyScroll, enableBodyScroll })

export function stopBodyScroll () {
    const scrollY = document.documentElement.style.getPropertyValue('--scroll-y');
    const body = document.body;
    body.style.position = 'fixed';
    body.style.top = `-${scrollY}`;
}

export function enableBodyScroll () {
    const body = document.body;
    const scrollY = body.style.top;
    body.style.position = '';
    body.style.top = '';
    window.scrollTo(0, parseInt(scrollY || '0') * -1);
}

// TODO(NS): can't we just grab window.scrollY when we run stopBodyScroll?
// TODO(NS): remove other definitions of stopBodyScroll/enableBodyScroll
window.addEventListener('scroll', () => {
    document.documentElement.style.setProperty('--scroll-y', `${window.scrollY}px`)
})