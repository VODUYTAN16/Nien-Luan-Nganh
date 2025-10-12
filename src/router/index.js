import { createRouter, createWebHistory } from 'vue-router';
// import HomeView from '../views/HomeView.vue';
import Discover from '@/views/Discover.vue';
// import Category from '@/views/Category.vue';
// import Borrowed from '@/views/Borrowed.vue';
// import BookDetail from '@/views/BookDetail.vue';
// import AddBook from '@/views/AddBook.vue';
// import BookPage from '@/components/BookPage.vue';
// import RegisterOrLogin from '@/components/RegisterOrLogin.vue';
// import Login from '@/components/LeafFall.vue';
// import UserManagement from '@/views/UserManagement.vue';
// import BooksManagement from '@/views/BooksManagement.vue';
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Discover',
      component: Discover,
    },
    // {
    //   path: '/category',
    //   name: 'Category',
    //   component: Category,
    // },
    // {
    //   path: '/borrowed',
    //   component: Borrowed,
    // },
    // {
    //   path: '/add-book',
    //   component: AddBook,
    // },
    // {
    //   path: '/books-management',
    //   component: BooksManagement,
    // },
    // {
    //   path: '/account',
    //   component: UserManagement,
    // },
    // {
    //   path: '/bookdetail/:masach', // Chúng ta sẽ truyền tham số fileId
    //   name: 'BookDetail',
    //   component: BookDetail,
    // },
  ],
});

export default router;
