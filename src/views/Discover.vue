<template>
  <div class="discover">
    <div class="box"><LeafFall></LeafFall></div>
    <div class="sidebar">
      <h1 class="mb-4">📖 Discover</h1>
      <form
        class="d-flex align-items-center bg-white shadow px-4 py-2 my-2 search-bar"
        style=""
      >
        <select
          v-model="selectedCategory"
          @change="onChangeCategory"
          class="me-2 form-select"
          style="border: none"
        >
          <option value="all">All</option>
          <option
            v-for="(item, index) in categories"
            :key="index"
            :value="item.madm"
            style="border: none"
          >
            {{ item.tendm }}
          </option>
        </select>
        <div class="vr mx-3"></div>
        <i class="bx bx-search-big"></i>

        <input
          v-model="searchQuery"
          placeholder="Find books by name"
          class="me-2 flex-grow-1 form-control"
        />

        <button
          variant="dark"
          @click.prevent="onSearch"
          class="btn btn-success px-3"
        >
          Search
        </button>
      </form>
      <div class="recommendation mt-5">
        <!-- <BookList :book_list="displayedBooks || []"></BookList> -->
      </div>
    </div>
  </div>
</template>

<script setup>
// import BookDetail from './BookDetail.vue';
// import BookList from '../components/BookList.vue';
import LeafFall from '../components/LeafFall.vue';
import { onMounted, ref } from 'vue';
import { _fetch_Book_List, _fetch_Category } from '../service/service';

const selectedCategory = ref('all');
const displayedBooks = ref([]);
const searchQuery = ref('');

const SachList = ref([]);
const categories = ref([]);

const onSearch = () => {
  const keyword = searchQuery.value.trim().toLowerCase();

  if (!keyword) {
    // Nếu không có từ khóa, hiển thị toàn bộ sách
    displayedBooks.value = SachList.value;
  } else {
    displayedBooks.value = SachList.value.filter((book) =>
      book.tensach?.toLowerCase().includes(keyword)
    );
  }

  console.log('Kết quả tìm kiếm:', displayedBooks.value);
};

const onChangeCategory = async () => {
  if (selectedCategory.value == 'all') {
    SachList.value = await _fetch_Book_List();
    displayedBooks.value = SachList.value;
  } else {
    SachList.value = await _fetch_Book_List(selectedCategory.value);
    displayedBooks.value = SachList.value;
  }
};

onMounted(async () => {
  console.log(history.state);
  if (history.state?.category) {
    selectedCategory.value = history.state?.category || '';
  }
  onChangeCategory();

  categories.value = await _fetch_Category();
  console.log(categories.value);
});
</script>
<style scoped>
.discover {
  position: relative;
  height: 100vh;
}

.box {
  position: absolute !important;
  top: 0;
  left: 0;
  width: 100%;
  height: 50vh;
  border-end-start-radius: 80px;
  background-color: var(--sub-bg);
  transform: translateY(-100%);
  animation: slideDown 0.8s ease-out forwards;
  overflow: hidden;
}
@keyframes slideDown {
  to {
    transform: translateY(0);
  }
}

.sidebar {
  position: absolute;
  top: 10%;
  left: 5%;
  width: 90%;
}
.form-control:focus {
  border-color: transparent; /* hoặc một màu khác */
  box-shadow: none;
  outline: none;
}
.form-control {
  border-color: transparent; /* hoặc một màu khác */
  box-shadow: none;
  outline: none;
}

.form-select:focus {
  border-color: transparent; /* hoặc một màu khác */
  box-shadow: none;
  outline: none;
}

form {
  border-radius: 5px;
  font-size: 25px;
  width: fit-content;
}
</style>
