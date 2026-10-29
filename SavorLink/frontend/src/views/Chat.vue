<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'

type ChatListItem = {
  id: number
  user1_id: number
  user2_id: number
  created_at: string
  user1?: { id: number; email: string } | null
  user2?: { id: number; email: string } | null
  last_message?: { content: string; created_at: string } | null
}

type MessageItem = {
  id: number
  sender_id: number
  content: string
  created_at: string
  sender?: { id: number; email: string } | null
}

type ChatItem = {
  id: number
  messages: MessageItem[]
  user1_id: number
  user2_id: number
  user1?: { id: number; email: string } | null
  user2?: { id: number; email: string } | null
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const chats = ref<ChatListItem[]>([])
const activeChat = ref<ChatItem | null>(null)
const messageText = ref('')
const loading = ref(false)
const loadingChat = ref(false)
const sending = ref(false)
const error = ref('')

const me = computed(() => authStore.user?.id ?? null)

const otherUser = (chat: ChatListItem | ChatItem) => {
  if (!me.value) return null
  const candidate = chat.user1_id === me.value ? chat.user2 : chat.user1
  return candidate ?? null
}

const loadChats = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await api.get('/chats')
    chats.value = response.data || []

    const firstChat = chats.value[0]
    if (!activeChat.value && firstChat) {
      await openChat(firstChat.id)
    }
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Не удалось загрузить список чатов'
  } finally {
    loading.value = false
  }
}

const openChat = async (chatId: number) => {
  loadingChat.value = true
  error.value = ''

  try {
    const response = await api.get(`/chats/${chatId}`)
    activeChat.value = response.data
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Не удалось открыть чат'
  } finally {
    loadingChat.value = false
  }
}

const sendMessage = async () => {
  if (!activeChat.value || !messageText.value.trim() || sending.value) return
  sending.value = true
  error.value = ''

  try {
    await api.post(`/chats/${activeChat.value.id}/messages`, { content: messageText.value.trim() })
    messageText.value = ''
    await openChat(activeChat.value.id)
    await loadChats()
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Не удалось отправить сообщение'
  } finally {
    sending.value = false
  }
}

const createChat = async (userId: number) => {
  if (!userId) return

  try {
    const response = await api.post('/chats', { user2_id: userId })
    await loadChats()
    await openChat(response.data.id)
    router.replace({ query: {} })
  } catch (err: any) {
    if (err.response?.status === 409 || err.response?.data?.detail?.includes('exists') || err.response?.data?.detail?.includes('существует')) {
      await loadChats()
      const existingChat = chats.value.find(c => c.user1_id === userId || c.user2_id === userId)
      if (existingChat) {
        await openChat(existingChat.id)
      }
      router.replace({ query: {} })
    } else {
      error.value = err?.response?.data?.detail || 'Не удалось создать чат'
    }
  }
}

const formatDate = (value: string) =>
  new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  await loadChats()

  if (route.query.userId) {
    const userId = Number(route.query.userId)
    if (userId) {
      const existingChat = chats.value.find(c => c.user1_id === userId || c.user2_id === userId)
      if (existingChat) {
        await openChat(existingChat.id)
        router.replace({ query: {} })
      } else {
        await createChat(userId)
      }
    }
  }
})
</script>

<template>
  <main class="chat-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Чат</p>
        <h1>Диалоги с контрагентами</h1>
        <p>Выберите чат из списка или перейдите в чат со страницы поставщика.</p>
      </div>
    </section>

    <div v-if="error" class="error-box">{{ error }}</div>

    <div class="chat-layout">
      <aside class="sidebar">
        <h2>Чаты</h2>
        <div v-if="loading" class="state-box">Загрузка...</div>
        <button
          v-for="chat in chats"
          :key="chat.id"
          class="chat-item"
          :class="{ active: activeChat?.id === chat.id }"
          @click="openChat(chat.id)"
        >
          <strong>{{ otherUser(chat)?.email || `Чат #${chat.id}` }}</strong>
          <span>{{ chat.last_message?.content || 'Нет сообщений' }}</span>
        </button>
      </aside>

      <section class="conversation">
        <div v-if="loadingChat" class="state-box">Открываем чат...</div>
        <div v-else-if="!activeChat" class="state-box">Выберите чат слева.</div>
        <template v-else>
          <header class="conversation-head">
            <div>
              <h2>{{ otherUser(activeChat)?.email || `Чат #${activeChat.id}` }}</h2>
              <p>{{ activeChat.messages.length }} сообщений</p>
            </div>
          </header>

          <div class="messages">
            <article v-for="message in activeChat.messages" :key="message.id" class="message">
              <div class="message-head">
                <strong>{{ message.sender?.email || `Пользователь #${message.sender_id}` }}</strong>
                <time>{{ formatDate(message.created_at) }}</time>
              </div>
              <p>{{ message.content }}</p>
            </article>
          </div>

          <div class="composer">
            <textarea v-model="messageText" rows="3" placeholder="Введите сообщение"></textarea>
            <button class="primary-btn" :disabled="sending" @click="sendMessage">
              {{ sending ? 'Отправка...' : 'Отправить' }}
            </button>
          </div>
        </template>
      </section>
    </div>
  </main>
</template>

<style scoped>
.chat-page {
  display: grid;
  gap: 1rem;
  padding-bottom: 2rem;
}

.hero,
.sidebar,
.conversation,
.error-box,
.state-box {
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(76, 124, 42, 0.14);
  border-radius: 1.5rem;
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.1);
}

.hero {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.eyebrow {
  margin: 0 0 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #5d6b52;
  font-size: 0.75rem;
}

.new-chat {
  display: grid;
  gap: 0.5rem;
  min-width: 220px;
  align-content: center;
}

.new-chat input,
textarea {
  width: 100%;
  padding: 0.8rem 0.9rem;
  border-radius: 1rem;
  border: 1px solid rgba(76, 124, 42, 0.14);
  background: rgba(255, 255, 255, 0.9);
}

.chat-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1rem;
}

.sidebar,
.conversation {
  padding: 1rem;
}

.sidebar {
  display: grid;
  gap: 0.7rem;
  align-content: start;
}

.chat-item {
  display: grid;
  gap: 0.25rem;
  text-align: left;
  padding: 0.85rem;
  border-radius: 1rem;
  border: 1px solid rgba(76, 124, 42, 0.14);
  background: rgba(255, 255, 255, 0.85);
  cursor: pointer;
}

.chat-item.active {
  background: rgba(191, 229, 158, 0.35);
}

.chat-item span {
  color: #5d6b52;
  font-size: 0.85rem;
}

.conversation {
  display: grid;
  gap: 1rem;
}

.conversation-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.messages {
  display: grid;
  gap: 0.75rem;
  max-height: 520px;
  overflow: auto;
  padding-right: 0.25rem;
}

.message {
  padding: 0.9rem 1rem;
  border-radius: 1rem;
  background: rgba(249, 250, 251, 0.75);
}

.message-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.35rem;
  color: #5d6b52;
  font-size: 0.85rem;
}

.message p {
  margin: 0;
}

.composer {
  display: grid;
  gap: 0.75rem;
}

.primary-btn {
  border: none;
  border-radius: 999px;
  padding: 0.9rem 1.2rem;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: #fff;
  font-weight: 800;
  cursor: pointer;
}

.error-box,
.state-box {
  padding: 1rem 1.15rem;
}

.error-box {
  color: #991b1b;
  background: #fee2e2;
}

@media (max-width: 900px) {
  .hero,
  .chat-layout {
    display: grid;
    grid-template-columns: 1fr;
  }
}
</style>
