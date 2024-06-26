<script setup lang="ts">
import RecordingPanel from '@/components/record-page/recording-panel.vue'
import Spinner from '@/components/ui/spinner.vue'
import RecordingDeviceSelect from '@/components/record-page/recording-device-select.vue'
import TranscriptionOptionsInputs from '../transcription-options-inputs.vue'

import { SpokenTextStats } from '@/types/spoken-text-stats'
import { useApi } from '@/composables/api'
import { reactive } from 'vue'

const { fetchWithErrorNotification } = useApi()

const counterForm = reactive({
    data: {
        inputDeviceIndex: null,
        wordListName: null,
        language: null,
    },
    loading: false,
})

const countingProcess = reactive<{
    secondsRunning?: number
    result?: SpokenTextStats
}>({
    /* secondsRunning: 0,
    result: {
        wordsStats: [...Array(100).fill({
            word: 'fasdfsdf',
            count: 343
        }), ...Array(2).fill({
            word: 'test',
            count: 1000
        })],
        fullText: 'fasdfsdf fasdfsdf fasdfsdf: fasdfsdf fasdfsdf fasdfsdf - fasdfsdf, '
            + 'fasdfsdf. fasdfsdffasdfsdf fasdfsdf'
    } */
})

let secondsCountingIntervalId: number | undefined = undefined

async function start() {
    counterForm.loading = true

    const response = await fetchWithErrorNotification('/realtime-counter', {
        method: 'POST',
        body: JSON.stringify({
            language: counterForm.data.language,
            recording_device_index: counterForm.data.inputDeviceIndex,
            word_list_name: counterForm.data.wordListName
        })
    })

    counterForm.loading = false

    if(!response.error) {
        countingProcess.secondsRunning = 0

        secondsCountingIntervalId = window.setInterval(() => {
            if(countingProcess.secondsRunning !== undefined) {
                countingProcess.secondsRunning += 1
            }

            updateResult()
        }, 1000)
    }
}

async function reset() {
    window.clearInterval(secondsCountingIntervalId)

    const response = await fetchWithErrorNotification('/realtime-counter', {
        method: 'DELETE'
    })

    if(!response.error) {
        countingProcess.secondsRunning = undefined
        countingProcess.result = undefined
    }
}

async function updateResult() {
    const response = await fetchWithErrorNotification('/realtime-counter/result', {
        method: 'GET'
    }, 'error while updating words statistics: ')

    if(response.data) {
        countingProcess.result = {
            wordsStats: response.data.words_stats,
            fullText: response.data.full_text
        }
    }
}
</script>

<template>
    <form
        v-if="countingProcess.secondsRunning === undefined"
        class="bg-neutral-100 rounded-lg max-w-[1080px] px-8 py-7 min-h-72"
        @submit.prevent="start"
    >
        <div
            v-if="!counterForm.loading"
            class="flex items-start gap-x-14 gap-y-8 sm:flex-wrap-reverse"
        >
            <button
                class="w-28 h-28 bg-white shadow-black/20 shadow-2xl rounded-full
                    flex items-center justify-center flex-shrink-0
                    transition-transform duration-300 hover:scale-105"
                title="start words counter"
            >
                <svg class="w-8" viewBox="0 0 33 44" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                        d="M8.5 8C8.5 3.58172 12.0817 0 16.5 0C20.9182 0 24.5 3.58172 24.5 8V22C24.5 26.4182 20.9182 30 16.5 30C12.0817 30 8.5 26.4182 8.5 22V8Z"
                        fill="#F75757" />
                    <path
                        d="M5 21.6876V22C5 25.05 6.2116 27.975 8.36828 30.1318C10.5249 32.2884 13.45 33.5 16.5 33.5C19.55 33.5 22.475 32.2884 24.6318 30.1318C26.7884 27.975 28 25.05 28 22V21.6876C28 20.583 28.8954 19.6876 30 19.6876H31C32.1046 19.6876 33 20.583 33 21.6874V22C33 26.376 31.2616 30.573 28.1672 33.6672C25.6684 36.1662 22.4506 37.7806 19 38.3096V42C19 43.1046 18.1046 44 17 44H16C14.8954 44 14 43.1046 14 42V38.3096C10.5494 37.7806 7.33158 36.1662 4.83274 33.6672C1.73838 30.573 0 26.376 0 22V21.6876C0 20.583 0.89544 19.6876 2 19.6876H3C4.10456 19.6876 5 20.583 5 21.6876Z"
                        fill="#F75757" />
                </svg>
            </button>

            <Suspense>
                <div class="flex-grow flex items-start gap-x-8 sm:gap-x-4 gap-y-8 flex-wrap">
                    <RecordingDeviceSelect
                        v-model:device-index="counterForm.data.inputDeviceIndex"
                    />
    
                    <TranscriptionOptionsInputs
                        v-model:language="counterForm.data.language"
                        v-model:word-list-name="counterForm.data.wordListName"
                    />
                </div>

                <template #fallback>
                    <Spinner/>
                </template>
            </Suspense>
        </div>

        <div v-else class="font-normal max-w-96 text-neutral-600">
            <Spinner class="mb-5" />
            loading model, it can take some time if you haven't used it previously
        </div>
    </form>

    <RecordingPanel
        v-else
        :seconds-passed="countingProcess.secondsRunning"
        :result="{
            fullText: countingProcess.result?.fullText || '',
            wordsStats: countingProcess.result?.wordsStats || []
        }"
        @reset="reset"
    />
</template>
