<template>
  <div class="mt-6">
    <h3 class="mb-3 text-base font-semibold">Comments</h3>

    <!-- Add Comment Form -->
    <div class="mb-6 rounded bg-surface-gray-1 p-3">
      <TextEditor
        v-model="newCommentContent"
        :content="newCommentContent"
        :editable="true"
        :mentions="usersList"
        :editor-class="['prose-sm max-w-none min-h-[3rem]']"
        @change="newCommentContent = $event"
      />
      <div class="mt-2 flex justify-end gap-2">
        <Button 
          :label="__('Cancel')" 
          @click="newCommentContent = ''"
          :disabled="!newCommentContent"
        />
        <Button
          variant="solid"
          :label="__('Add Comment')"
          :loading="addingComment"
          @click="submitComment"
          :disabled="!newCommentContent"
        />
      </div>
    </div>

    <!-- Comments List -->
    <div v-if="comments.length" class="space-y-4">
      <div
        v-for="(comment, i) in comments"
        :key="comment.name"
        class="activity grid grid-cols-[30px_minmax(auto,_1fr)] gap-2 sm:gap-4"
      >
        <!-- Timeline -->
        <div
          class="z-0 relative flex justify-center before:absolute before:left-[50%] before:-z-[1] before:top-0 before:border-l before:border-outline-elevation-2"
          :class="i != comments.length - 1 ? 'before:h-full' : 'before:h-4'"
        >
          <div class="flex h-8 w-7 items-center justify-center bg-surface-base">
            <CommentIcon class="text-ink-gray-8" />
          </div>
        </div>

        <!-- Comment Content -->
        <div class="mb-4">
          <div class="mb-1 flex items-center justify-stretch gap-2 py-1 text-base">
            <div class="inline-flex items-center flex-wrap gap-1 text-ink-gray-5">
              <UserAvatar :user="comment.owner" size="md" />
              <span class="font-medium text-ink-gray-8">
                {{ comment.owner_name }}
              </span>
              <span>{{ __('added a comment') }}</span>
            </div>
            <div class="ml-auto flex items-center gap-1 whitespace-nowrap">
              <TimelineTimestamp :date="comment.creation" />
              <Dropdown
                v-if="isCommentOwner(comment) && !editingCommentId"
                :options="getCommentMenuOptions(comment)"
                placement="right"
              >
                <Button
                  icon="lucide-more-horizontal"
                  variant="ghost"
                  class="!h-6 !w-6"
                />
              </Dropdown>
            </div>
          </div>

          <!-- Comment Body -->
          <div
            class="rounded bg-surface-gray-1 px-3 py-[7.5px] text-base leading-6 transition-all duration-300 ease-in-out"
          >
            <template v-if="editingCommentId === comment.name">
              <TextEditor
                :content="editContent"
                :editable="true"
                :mentions="usersList"
                :editor-class="['prose-sm max-w-none min-h-[3rem]']"
                @change="editContent = $event"
              />
              <div class="mt-2 flex justify-end gap-2">
                <Button :label="__('Cancel')" @click="cancelEdit" />
                <Button
                  variant="solid"
                  :label="__('Save')"
                  :loading="savingComment"
                  @click="saveEdit(comment)"
                />
              </div>
            </template>
            <template v-else>
              <!-- eslint-disable-next-line vue/no-v-html -->
              <div class="prose-f" v-html="sanitizeHTML(comment.content)" />
              <div
                v-if="comment.attachments?.length"
                class="mt-2 flex flex-wrap gap-2"
              >
                <AttachmentItem
                  v-for="a in comment.attachments"
                  :key="a.file_url"
                  :label="a.file_name"
                  :url="a.file_url"
                />
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-sm text-gray-500 text-center py-8">
      {{ __('No comments yet. Be the first to add one!') }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { call, toast, TextEditor, Button, Dropdown } from "frappe-ui"
import UserAvatar from "@/components/UserAvatar.vue"
import AttachmentItem from "@/components/AttachmentItem.vue"
import TimelineTimestamp from "@/components/Activities/TimelineTimestamp.vue"
import CommentIcon from "@/components/Icons/CommentIcon.vue"
import { sanitizeHTML, ConfirmDelete } from "@/utils"
import { sessionStore } from "@/stores/session"
import { usersStore } from '@/stores/users'

const props = defineProps({
  ticket: {
    type: String,
    required: true,
  },
})

const { user } = sessionStore()
const { users: usersList } = usersStore()
console.log("Users List:", usersList)

const comments = ref([])
const newCommentContent = ref("")
const addingComment = ref(false)
const editingCommentId = ref(null)
const editContent = ref("")
const savingComment = ref(false)
const confirmingDeleteId = ref(null)

async function loadComments() {
  try {
    comments.value = await call(
      "crm.fcrm.doctype.tickets.tickets.get_comments",
      {
        ticket: props.ticket,
      }
    )
  } catch (error) {
    console.error("Failed to load comments:", error)
    toast.error(__("Failed to load comments"))
  }
}

async function submitComment() {
  if (!newCommentContent.value.trim()) {
    return
  }

  addingComment.value = true
  try {
    await call(
      "crm.fcrm.doctype.tickets.tickets.add_comment",
      {
        ticket: props.ticket,
        content: newCommentContent.value,
      }
    )
    toast.success(__("Comment added"))
    newCommentContent.value = ""
    await loadComments()
  } catch (error) {
    console.error("Failed to add comment:", error)
    toast.error(__("Failed to add comment"))
  } finally {
    addingComment.value = false
  }
}

function isCommentOwner(comment) {
  return comment.owner === user
}

function startEdit(comment) {
  editingCommentId.value = comment.name
  editContent.value = comment.content || ""
}

function cancelEdit() {
  editingCommentId.value = null
  editContent.value = ""
  confirmingDeleteId.value = null
}

async function saveEdit(comment) {
  if (editContent.value === comment.content) {
    editingCommentId.value = null
    return
  }

  savingComment.value = true
  try {
    await call("frappe.client.set_value", {
      doctype: "Comment",
      name: comment.name,
      fieldname: "content",
      value: editContent.value,
    })
    toast.success(__("Comment updated"))
    editingCommentId.value = null
    await loadComments()
  } catch (error) {
    console.error("Failed to update comment:", error)
    toast.error(__("Failed to update comment"))
  } finally {
    savingComment.value = false
  }
}

async function deleteComment(comment) {
  try {
    await call("frappe.client.delete", {
      doctype: "Comment",
      name: comment.name,
    })
    toast.success(__("Comment deleted"))
    await loadComments()
  } catch (error) {
    console.error("Failed to delete comment:", error)
    toast.error(__("Failed to delete comment"))
  }
}

function getCommentMenuOptions(comment) {
  return [
    {
      label: __("Edit"),
      icon: "edit-2",
      onClick: () => startEdit(comment),
    },
    ...ConfirmDelete({
      onConfirmDelete: () => deleteComment(comment),
      isConfirmingDelete: computed({
        get: () => confirmingDeleteId.value === comment.name,
        set: (val) => {
          confirmingDeleteId.value = val ? comment.name : null
        },
      }),
    }),
  ]
}

onMounted(() => {
  loadComments()
})
</script>