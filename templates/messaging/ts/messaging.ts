import htmx from "htmx.org"

import Alpine from "alpinejs";
import {expose} from "@/templates/ts/utils.ts";

/*
    As part of the proof-of-concept there are TWO ways to use setupMessageRefresh

    1. Calling the function in x-init, e.g.

        x-init="setupMessageRefresh(`{{ message_count_url }}`, `{{ message_list_url }}`, `messages-{{ unique_id }}`)"

    2. Using the "x-setup-message-refresh" directive, e.g.:

        x-setup-message-refresh="[`{{ message_count_url }}`, `{{ message_list_url }}`, `messages-{{ unique_id }}`]"

        This one is probably the best one, as we have access to the element
        it is on (although not currently used in this POC)

 */

expose({ setupMessageRefresh })

Alpine.directive('setup-message-refresh', (_, { expression }, { evaluate }) => {
    const [messageCountURL, messageListURL, messageListTargetId]: [string, string, string] = evaluate(expression) as any
    setupMessageRefresh(messageCountURL, messageListURL, messageListTargetId)
})

function setupMessageRefresh(messageCountURL: string, messageListURL: string, messageListTargetId: string) {
    let lastCount: number = 0

    // Get the initial value
    fetchMessageCount().then(count => {
        lastCount = count
    })

    setInterval(async () => {
        if (isActive()) {
            // We are active \o/
            // Go and check and refresh messages if changed
            const count = await fetchMessageCount()
            if (count !== lastCount) {
                lastCount = count
                await refreshMessageList()
            }
        }
    }, 4000)

    async function fetchMessageCount(): Promise<number> {
        return Number(await getText(messageCountURL))
    }

    async function getText(url: string): Promise<string> {
        return new Promise(resolve => {
            htmx.ajax('GET', url, {
                handler (_: any, obj: any) {
                    resolve(obj.xhr.responseText)
                },
            })
        })
    }

    async function refreshMessageList() {
        await htmx.ajax('GET', messageListURL, `#${messageListTargetId}`)
        const elem = document.getElementById(messageListTargetId)?.closest('.drawer-contents')
        if (elem) {
            scrollToBottom(elem)
        }
    }

    function isActive() {
        const elem = document.getElementById(messageListTargetId)
        if (!elem) return false
        return (
            // Whole document is visible
            document.visibilityState === 'visible' &&
            // We're in a "selected" thing (defined in drawer-river)
            elem.classList.contains('selected') &&
            // The message list is visible (on the right tab)
            isElementVisible(elem)
        )
    }

    function isElementVisible (elem: HTMLElement) {
        // borrowed from jQuery logic
        return !!( elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length );
    }

    function scrollToBottom(elem: Element) {
        elem.scrollTop = elem.scrollHeight;
    }
}