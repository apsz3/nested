(include ./math.al) -- defines `len` and `empty?`

(let filter (lambda (fn ls)
    (if (empty? ls)
        'empty
        (if (fn (fst ls))
            (cons (fst ls) (filter fn (rst ls)))
            (filter fn (rst ls))))))

(defmacro asseq (a b) (assert (= a b))) -- Macro expansion happens at compile time

(asseq (len (filter (lambda (x) (< x 3)) '(1 2 3))) 2)

(let fib (lambda (n)
    (if (= n 0) 0
    (if (= n 1) 1
        (+ (fib (- n 1)) (fib (- n 2)))))))

(asseq (fib 10) 55)