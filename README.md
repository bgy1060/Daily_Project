# Daily_Project_Back

## 1. **개요**

- Daily_Now는 P2P 투자자들을 대상으로 만든 P2P 투자 정보 모아보기 서비스를 제공한다.
- 사용자는 자신이 가입한 P2P 사이트 로그인 / 비밀번호를 Daily_Now 사이트에 등록한 후 자신의 투자 정보를 한 번에 모아서 볼 수 있다.

<br/>

## 2. 기술 Stack

- **FrontEnd** 
  - React.js
- **BackEnd** 
  - Django REST framework
- **Scraping** 
  - request & selenium
  - Kakao OCR API
- **Encryption**
  - AES 256
- **Software Distribution**
  - Naver Cloud Platform

<br/>

## 3. Database Schema

![img](https://lh5.googleusercontent.com/45EJZK3RP9Yr0hCqz9wifbzgE3Nx755cQNlnSM98qVbcyZzpRdfyQei5HsczgXxLGErU94DR3WUhugRg8WxAq3MKVg0z8gN7HIy4X7e3rnPlLYfT6Yu3oxbKB3LPAInR4AV2qyF1)

각 테이블은 다음과 같이 설계되었다.

1. **register** : id, uid, company_id, username, user_password
2. **p2p_company** : id, company_name, homepage_url, nickname
3. **deposit and withdrawal** : id, uid, company_id, transaction_amount, remaining_amount, trading_time
4. **account** : id, uid, company_id, account_holder, bank, account_number, deposit
5. **summary_investing** : id, uid, company_id, investing_product, investing_price, investing_time, status, investing_type
6. **investment_balance** : id, uid, company_id, total_investment, number_of_investing_products, residual_investment_price
7. **notice_board**: post_id, uid, title, content, date, views, like, dislike
8. **user**: uid, username, password, name, email, date_joined, withdrawal_status, withdrawal_date
9. **investing_status** : status_code, status_meaning
10. **investing_type** : type_code, type_meaning
11. **comment** : comment_id, post_id, parent_comment, uid, comment_content, date, like, dislike
12. **comment_like** : id, comment_id, parent_comment, uid, like_dislike
13. **FAQ** : id, question, answer, view, order
14. **notice_board_like** : id, post_id, uid, like_dislike
15. **point_action** : id, action, point_value, limited_number_of_day
16. **point_list** : id, action_id, uid, point, total_point, date, detail_action

<br/>

## 4. 결과물

- 사용자 메뉴얼 
  - [메뉴얼](https://github.com/bgy1060/Daily_Project/blob/main/Daily%20Now%20%EC%82%AC%EC%9A%A9%EC%9E%90%20MANUAL.md)
- 사이트 링크
  - http://49.50.163.188:3000/
