<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template v-if="!errorTitle" #right-header>
      <CustomActions
        v-if="document._actions?.length"
        :actions="document._actions"
      />
      <CustomActions
        v-if="document.actions?.length"
        :actions="document.actions"
      />
      <AssignTo v-model="assignees.data" :doctype="doctype" :docname="ticketId" />
    </template>
  </LayoutHeader>
  <div v-if="doc.name" class="flex h-full overflow-hidden">
    <Tabs
      v-model="tabIndex" 
      :tabs="tabs"
      class="flex flex-1 overflow-hidden flex-col [&_[role='tab']]:px-0 [&_[role='tab']]:shrink-0 [&_[role='tablist']]:px-5 [&_[role='tablist']::-webkit-scrollbar]:h-0 [&_[role='tablist']]:min-h-[45px] [&_[role='tablist']]:gap-7.5 [&_[role='tabpanel']:not([hidden])]:flex [&_[role='tabpanel']:not([hidden])]:grow"
    >
      <template #tab-panel>
        <Activities
          ref="activities"
          v-model:reload="reload"
          v-model:tabIndex="tabIndex"
          :doctype="doctype"
          :docname="ticketId"
          :tabs="tabs"
          @afterSave="reloadResources"
        />
      </template>
    </Tabs>
    <Resizer class="flex flex-col justify-between border-l" side="right">
      <div
        class="flex h-[45px] cursor-copy items-center border-b px-5 py-2.5 text-lg-medium text-ink-gray-9"
        @click="copyToClipboard(ticketId)"
      >
        {{ __(ticketId) }}
      </div>
      <FileUploader
        :validateFile="validateIsImageFile"
        @success="(file) => updateField('image', file.file_url)"
      >
        <template #default="{ openFileSelector }">
          <div class="flex items-center justify-start gap-5 border-b p-5">
            <div class="group relative size-12">
              <Avatar
                size="3xl"
                class="size-12"
                :label="title"
                :image="doc.image"
              />
              <component
                :is="doc.image ? Dropdown : 'div'"
                v-bind="
                  doc.image
                    ? {
                        options: [
                          {
                            icon: 'upload',
                            label: doc.image
                              ? __('Change Image')
                              : __('Upload Image'),
                            onClick: openFileSelector,
                          },
                          {
                            icon: 'trash-2',
                            label: __('Remove Image'),
                            onClick: () => updateField('image', ''),
                          },
                        ],
                      }
                    : { onClick: openFileSelector }
                "
                class="!absolute bottom-0 left-0 right-0"
              >
                <div
                  class="z-1 absolute bottom-0.5 left-0 right-0.5 flex h-9 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-3 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
                  style="-webkit-clip-path: inset(12px 0 0 0); clip-path: inset(12px 0 0 0);"
                >
                  <CameraIcon class="size-4 cursor-pointer text-white" />
                </div>
              </component>
            </div>
            <div class="flex flex-col gap-2.5 truncate">
              <Tooltip :text="doc.title || __('Set Title')">
                <div class="truncate text-3xl-medium text-ink-gray-9">
                  {{ title }}
                </div>
              </Tooltip>
              <div class="flex gap-1.5">
                <Button
                  :tooltip="__('Send an Email')"
                  :icon="Email2Icon"
                  @click="doc.email ? openEmailBox() : toast.error(__('Please set an email address to send emails'))"
                />
                <Button
                  :tooltip="__('Attach a File')"
                  :icon="AttachmentIcon"
                  @click="showFilesUploader = true"
                />
                <Button
                  v-if="canDelete"
                  :tooltip="__('Delete')"
                  variant="subtle"
                  theme="red"
                  icon="lucide-trash-2"
                  @click="deleteTicket"
                />
              </div>
              <ErrorMessage :message="__(error)" />
            </div>
          </div>
        </template>
      </FileUploader>
      <div v-if="sections.data" class="flex flex-1 flex-col justify-between overflow-hidden">
        <SidePanelLayout
          :sections="sections.data"
          :doctype="doctype"
          :docname="ticketId"
          @reload="sections.reload"
          @afterFieldChange="reloadResources"
        />
      </div>
    </Resizer>
  </div>
  <ErrorPage v-else-if="errorTitle" :errorTitle="errorTitle" :errorMessage="errorMessage" />
  <FilesUploader
    v-model="showFilesUploader"
    :doctype="doctype"
    :docname="ticketId"
    @after="() => { activities?.all_activities?.reload(); changeTabTo('attachments') }"
  />
</template>

<script setup>
import ErrorPage from '@/components/ErrorPage.vue'
import Icon from '@/components/Icon.vue'
import Resizer from '@/components/Resizer.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
import EventIcon from '@/components/Icons/EventIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Activities from '@/components/Activities/Activities.vue'
import AssignTo from '@/components/AssignTo.vue'
import FilesUploader from '@/components/FilesUploader/FilesUploader.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import CustomActions from '@/components/CustomActions.vue'
import { openWebsite, setupCustomizations, copyToClipboard, validateIsImageFile } from '@/utils'
import { getView } from '@/utils/view'
import { getSettings } from '@/stores/settings'
import { globalStore } from '@/stores/global'
import { getMeta } from '@/stores/meta'
import { useDocument } from '@/data/document'
import { createResource, FileUploader, Dropdown, Tooltip, Avatar, Tabs, Breadcrumbs, call, usePageMeta, toast } from 'frappe-ui'
import { whatsappEnabled } from '@/composables/whatsapp'
import { useActiveTabManager } from '@/composables/useActiveTabManager'
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const doctype = 'Tickets'
const { brand } = getSettings()
const { $dialog, $socket } = globalStore()
const { doctypeMeta } = getMeta(doctype)

const props = defineProps({
  ticketId: { type: String, required: true },
})

const ticketId = props.ticketId
const reload = ref(false)
const activities = ref(null)
const errorTitle = ref('')
const errorMessage = ref('')
const showFilesUploader = ref(false)

const { triggerOnChange, triggerOnRender, assignees, permissions, document, scripts, error } = useDocument(doctype, ticketId)

const canDelete = computed(() => permissions.data?.permissions?.delete || false)

const doc = computed(() => document.doc || {})

onMounted(async () => {
  if (document.doc) await triggerOnRender()
})

watch(error, (err) => {
  if (err) {
    errorTitle.value = __('Error occurred')
    errorMessage.value = __(err.messages?.[0] || 'An error occurred')
  } else {
    errorTitle.value = ''
    errorMessage.value = ''
  }
})

watch(
  () => document.doc,
  async (_doc) => {
    if (scripts.data?.length) {
      let s = await setupCustomizations(scripts.data, {
        doc: _doc,
        $dialog,
        $socket,
        toast,
        updateField,
        createToast: toast.create,
        deleteDoc: deleteTicket,
        call,
      })
      document._actions = s.actions || []
    }
  },
  { once: true },
)

const breadcrumbs = computed(() => [{ label: __('Tickets'), route: { name: 'Tickets' } }, { label: title.value, route: { name: 'Ticket', params: { ticketId } } }])

const title = computed(() => {
  let t = doctypeMeta.value?.title_field || 'name'
  return doc.value?.[t] || ticketId
})

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'Tickets'],
  params: { doctype: 'Tickets' },
  auto: true,
})

const tabs = computed(() => {
  const tabOptions = [
    { name: 'activity', label: __('Activity'), icon: ActivityIcon },
    { name: 'emails', label: __('Emails'), icon: EmailIcon },
    { name: 'comments', label: __('Comments'), icon: CommentIcon },
    { name: 'data', label: __('Data'), icon: DetailsIcon },
    { name: 'events', label: __('Events'), icon: EventIcon },
    { name: 'calls', label: __('Calls'), icon: PhoneIcon },
    { name: 'tasks', label: __('Tasks'), icon: TaskIcon },
    { name: 'notes', label: __('Notes'), icon: NoteIcon },
    { name: 'attachments', label: __('Attachments'), icon: AttachmentIcon },
    { name: 'whatsapp', label: __('WhatsApp'), icon: WhatsAppIcon, condition: () => whatsappEnabled.value },
  ]

  return tabOptions.filter((t) => (t.condition ? t.condition() : true))
})

const { tabIndex, changeTabTo } = useActiveTabManager(tabs, 'lastTicketTab')

usePageMeta(() => ({ title: title.value, icon: brand.favicon }))

function reloadResources() {
  activities?.reload?.()
}

function updateField(field, value) {
  // useDocument exposes document.save
  document.save.submit(null, {
    onSuccess: () => {
      reloadResources()
    },
  })
}

async function deleteTicket() {
  await call('frappe.client.delete', {
    doctype,
    name: ticketId,
  })
}

</script>
