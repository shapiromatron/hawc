test_that("sillySum adds", {
  # numbers add
  expect_equal(sillySum(2, 3), 5)
  # string-like numbers add
  expect_equal(sillySum("2", "3"), 5)
})
