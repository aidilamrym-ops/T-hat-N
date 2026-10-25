from msaf.learnharness_prototype import LearnEngine


def test_engine_train_and_predict() -> None:
    engine = LearnEngine()
    assert engine.train([1, 2, 3]) == 3
    matrix = engine.predict(None)
    assert len(matrix) == 8
    assert all(len(row) == 8 for row in matrix)
    assert all(matrix[i][i] == 1 for i in range(8))
    assert all(matrix[i][j] == 0 for i in range(8) for j in range(8) if i != j)
