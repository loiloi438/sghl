import { computed } from 'vue'
import { filterNavigation, modulesByCategory as buildModulesByCategory } from '../config/navigation.js'
import { useAuthStore } from '../stores/auth.js'

export function useNavigation() {
  const auth = useAuthStore()

  const navigation = computed(() => filterNavigation(auth.role))
  const modulesByCategory = computed(() => buildModulesByCategory(auth.role))

  return { navigation, modulesByCategory }
}
