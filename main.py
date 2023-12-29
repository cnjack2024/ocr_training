import datetime
import os
import shutil

from pathlib import Path


def get_font_char(font):
    from fontTools.ttLib import TTFont

    data = set()

    for k in TTFont(font).getBestCmap():
        ch = chr(k)

        data.add(ch)

    print(len(data))

    with open("chi_sim.txt", "w") as f:
        for x in sorted(data):
            f.write(x)


class Train:
    def __init__(self):
        self.chi_sim = Path("chi_sim").resolve()
        self.fonts = Path("fonts").resolve()
        self.default_font_name = "SimSun"
        self.langdata_lstm = Path("langdata_lstm").resolve()
        self.tessdata = Path("tessdata_best").resolve()

        self.output = Path("output").resolve()
        self.eval = Path("eval").resolve()
        self.tmp = Path("tmp").resolve()

    def train(self):
        if not self.make_unicharset():
            return False

        if not self.make_starter_traineddata():
            return False

        return True

    def make_unicharset(self):
        """
        生成字符集lstm-unicharset文件
        """

        self.output.mkdir(parents=True, exist_ok=True)

        cmd = "unicharset_extractor --norm_mode 3 --output_unicharset {} {}".format(
            self.output.joinpath("chi_sim.lstm-unicharset").as_posix(),
            self.chi_sim.joinpath("chi_sim.txt").as_posix(),
        )

        os.system(cmd)

        if self.output.joinpath("chi_sim.lstm-unicharset").is_file():
            print("生成字符集lstm-unicharset文件成功")

            return True

        print("生成字符集lstm-unicharset文件失败")

        return False

    def make_starter_traineddata(self):
        """
        生成starter traineddata文件
        """

        number = 0

        with open(self.output.joinpath("chi_sim.lstm-unicharset").as_posix()) as f:
            for line in f:
                number = int(line.strip())

                break

        cmd = 'combine_lang_model --input_unicharset {} --lang chi_sim --script_dir {} --output_dir {} --version_str "{}" --words {} --numbers {} --puncs {} --pass_through_recoder'.format(
            self.output.joinpath("chi_sim.lstm-unicharset").as_posix(),
            self.langdata_lstm.as_posix(),
            self.output.as_posix(),
            f"watt:{datetime.date.today().strftime('%Y%m')}[1,48,0,1C3,3Ft16Mp3,3TxyLfys64Lfx96RxLrx96Lfx512O1c{number}]",
            self.langdata_lstm.joinpath("chi_sim", "chi_sim.wordlist").as_posix(),
            self.chi_sim.joinpath("chi_sim.numbers").as_posix(),
            self.chi_sim.joinpath("chi_sim.punc").as_posix(),
        )

        os.system(cmd)

        if self.output.joinpath("chi_sim", "chi_sim.traineddata").is_file():
            cmd = "combine_tessdata -d {}".format(
                self.output.joinpath("chi_sim", "chi_sim.traineddata")
            )

            if os.system(cmd) == 0:
                print("生成starter traineddata文件成功")

                return True

        shutil.rmtree(self.output.joinpath("chi_sim"), ignore_errors=True)

        print("生成starter traineddata文件失败")

        return False

    def make_train_tif(self, font_name=None):
        """
        生成train_tif文件
        """

        if not font_name:
            font_name = self.default_font_name

        output = self.output.joinpath(font_name.replace(" ", ""))

        self.output.mkdir(parents=True, exist_ok=True)
        self.tmp.mkdir(parents=True, exist_ok=True)

        cmd = 'text2image --text {} --outputbase {} --fonts_dir {} --font "{}" --ptsize 18 --fontconfig_tmpdir {}'.format(
            self.langdata_lstm.joinpath("chi_sim", "chi_sim.training_text").as_posix(),
            output.joinpath("train").as_posix(),
            self.fonts.as_posix(),
            font_name,
            self.tmp.as_posix(),
        )

        os.system(cmd)

        if output.joinpath("train.tif").is_file():
            print("生成train_tif文件成功")

            return True

        print("生成train_tif文件失败")

        return False

    def make_lstm_train(self, font_name=None):
        """
        生成训练文件
        """

        os.environ["TESSDATA_PREFIX"] = self.tessdata.as_posix()

        if not font_name:
            font_name = self.default_font_name

        output = self.output.joinpath(font_name.replace(" ", ""))

        cmd = "tesseract {} {} -l chi_sim --psm 6 {}/lstm.train".format(
            output.joinpath("train.tif").as_posix(),
            output.joinpath("train").as_posix(),
            self.chi_sim.as_posix(),
        )

        os.system(cmd)

        if output.joinpath("train.lstmf").is_file():
            print("生成训练文件成功")

            return True

        print("生成训练文件失败")

        return False

    def make_training(self):
        """
        训练
        """

        number = 0

        with open(self.output.joinpath("chi_sim.lstm-unicharset").as_posix()) as f:
            for line in f:
                number = int(line.strip())

                break

        with open(self.output.joinpath("train_listfile.txt").as_posix(), "w") as f:
            for file in self.output.glob("*/train.lstmf"):
                f.write(file.resolve().as_posix() + "\n")

        cmd = 'lstmtraining --traineddata {} --net_spec "{}" --model_output {} --train_listfile {} --max_iterations 0 --target_error_rate 0.0001 --debug_interval -1'.format(
            self.output.joinpath("chi_sim", "chi_sim.traineddata").as_posix(),
            f"[1,48,0,1Ct3,3,16 Mp3,3 Lfys64 Lfx96 Lrx96 Lfx512 O1c{number}]",
            self.output.joinpath("output").as_posix(),
            self.output.joinpath("train_listfile.txt").as_posix(),
        )

        os.system(cmd)

        if self.output.joinpath("output_checkpoint").is_file():
            print("训练成功")

            return True

        print("训练失败")

        return False

    def make_eval(self, font_name=None):
        """
        评估
        """

        os.environ["TESSDATA_PREFIX"] = self.tessdata.as_posix()

        if not font_name:
            font_name = self.default_font_name

        self.eval.mkdir(parents=True, exist_ok=True)
        self.tmp.mkdir(parents=True, exist_ok=True)

        cmd = 'text2image --text {} --outputbase {} --fonts_dir {} --font "{}" --ptsize 18 --fontconfig_tmpdir {}'.format(
            self.chi_sim.joinpath("eval.txt").as_posix(),
            self.eval.joinpath("eval").as_posix(),
            self.fonts.as_posix(),
            font_name,
            self.tmp.as_posix(),
        )

        os.system(cmd)

        if not self.eval.joinpath("eval.tif").is_file():
            print("评估失败(eval.tif)")

            return False

        cmd = "tesseract {} {} -l chi_sim --psm 6 {}/lstm.train".format(
            self.eval.joinpath("eval.tif").as_posix(),
            self.eval.joinpath("eval").as_posix(),
            self.chi_sim.as_posix(),
        )

        os.system(cmd)

        if not self.eval.joinpath("eval.lstmf").is_file():
            print("评估失败(eval.lstmf)")

            return False

        with open(self.eval.joinpath("eval_listfile.txt").as_posix(), "w") as f:
            f.write(self.eval.joinpath("eval.lstmf").as_posix() + "\n")

        cmd = "lstmeval --model {} --traineddata {} --eval_listfile {}".format(
            self.output.joinpath("output_checkpoint").as_posix(),
            self.eval.joinpath("chi_sim.traineddata").as_posix(),
            self.eval.joinpath("eval_listfile.txt"),
        )

        os.system(cmd)

        print("评估成功")

        return True

    def make_traineddata(self):
        """
        生成标准traineddata
        """

        cmd = "lstmtraining --stop_training --continue_from {} --traineddata {} --model_output {}".format(
            self.output.joinpath("output_checkpoint").as_posix(),
            self.chi_sim.joinpath("chi_sim.traineddata").as_posix(),
            self.output.joinpath("chi_sim.traineddata").as_posix(),
        )

        os.system(cmd)

        if self.output.joinpath("chi_sim.traineddata").is_file():
            print("生成成功")

            return True

        print("生成失败")

        return False


if __name__ == "__main__":
    # get_font_char("fonts/SimSun.ttf")

    train = Train()
    train.train()

    # train.make_lstm_train()
    # train.make_training()
    # train.make_eval()
    # train.make_traineddata()
