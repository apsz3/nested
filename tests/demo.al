(let asseq (lambda (a b) (assert (= a b))))

(let empty? (lambda (ls) (= ls 'empty)))
(let len (lambda (ls)
    (if (empty? ls)
        0
        (+ 1 (len (rst ls))))))

(let filter (lambda (fn ls)
    (if (empty? ls)
        'empty
        (if (fn (fst ls))
            (cons (fst ls) (filter fn (rst ls)))
            (filter fn (rst ls))))))
(print (filter (lambda (x) (< x 5)) (list 1 2 3 4 5 6 7 8 9 10)))
(let concat (lambda (ls1 ls2)
    (if (empty? ls1)
        ls2
        (cons (fst ls1) (concat (rst ls1) ls2)))))

;; (print (foo 3))  ; Should print 5
(let min (lambda (ls) (begin
    (let _min (lambda
        (ls m)
        (if (empty? ls)
            m
            (if (< (hd ls) m)
                (_min (rst ls) (hd ls))
                (_min (rst ls) m)))))
    (_min ls (fst ls)))))
(print (min (list 3 10 51 891 2)))

;; (let quicksort (lambda (ls)
;;     (if (empty? ls)
;;         'empty
;;         (begin
;;             (let pivot (fst ls))
;;             (print pivot)
;;             (concat
;;                 (quicksort (filter (lambda (x) (< x pivot)) (rst ls)))
;;                 'empty)))))
;; (print (quicksort (list 3 1 4 1 5 9 2 6 5 3 5)))
;; ;; (asseq (quicksort (list 3 1 4 1 5 9 2 6 5 3 5)) (list 1 1 2 3 3 4 5 5 5 6 9))