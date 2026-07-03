<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Tickets" />
    </template>
    <template #right-header>
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="createTicket"
      />
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="tickets"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Tickets"
  />
  <ListView
    v-if="tickets.data && rows.length"
    :rows="rows"
    :columns="columns"
    :options="{
      onRowClick: (row) => showModal({ doctype: 'Tickets', name: row.name, title: 'Ticket', callbacks: { afterInsert: () => tickets.value.reload?.(), afterUpdate: () => tickets.value.reload?.() } }),
      showTooltip: false,
      resizeColumn: true,
      rowCount: tickets.data.row_count,
      totalCount: tickets.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <EmptyState
    v-else-if="tickets.data && !rows.length"
    name="Tickets"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import { useDoctypeModal } from '@/composables/doctypeModal'
import { getMeta } from '@/stores/meta'
import { formatDate } from '@/utils'
import { timestampCell } from '@/composables/useTimelinePreferences'
import { ListView } from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import EmptyState from '../components/ListViews/EmptyState.vue'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('Ticket')
const { showModal } = useDoctypeModal()
const router = useRouter()

function createTicket() {
  showModal({
    doctype: 'Tickets',
    title: 'Ticket',
    callbacks: {
      afterInsert: () => tickets.value.reload?.(),
      afterUpdate: () => tickets.value.reload?.(),
    },
  })
}

// tickets data is loaded in the ViewControls component
const tickets = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const rows = computed(() => {
  if (
    !tickets.value?.data?.data ||
    !['list', 'group_by'].includes(tickets.value.data.view_type)
  )
    return []
  return tickets.value?.data.data.map((ticket) => {
    let _rows = {}
    tickets.value?.data.rows.forEach((row) => {
      _rows[row] = ticket[row]

      let fieldType = tickets.value?.data.columns?.find(
        (col) => (col.key || col.value) == row,
      )?.type

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation'].includes(row)
      ) {
        _rows[row] = formatDate(ticket[row], '', true, fieldType == 'Datetime')
      }

      if (fieldType == 'Currency') {
        _rows[row] = getFormattedCurrency(row, ticket)   
      }
      if (fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, ticket)
      }
      if (fieldType == 'Percent') {
        _rows[row] = getFormattedPercent(row, ticket)
      }
      if (['modified', 'creation'].includes(row)) {
        _rows[row] = timestampCell(ticket[row])
      }
    })
    return _rows
  })
})

const columns = computed(() => {
  let _columns = tickets.value?.data?.columns || []
  if (_columns.length) {
    _columns = _columns.map((col, index) => {
      if (index === _columns.length - 1) {
        return { ...col, align: 'right' }
      }
      return col
    })
  }
  return _columns
})
</script>